import logging

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import role_required
from .models import Payment


logger = logging.getLogger('fooddelivery')


def _can_view_payment(user, payment):
	return user.is_authenticated and (user.role == 'admin' or payment.order.customer_id == user.id)


@role_required(['admin', 'client'])
def payment_detail(request, pk):
	payment = get_object_or_404(Payment, pk=pk)

	if not _can_view_payment(request.user, payment):
		raise Http404('Payment not found')

	return render(request, 'payments/payment_detail.html', {
		'payment': payment,
		'can_manage': request.user.role == 'admin',
	})


@role_required(['admin'])
def payment_confirm(request, pk):
	payment = get_object_or_404(Payment, pk=pk)

	if payment.method != Payment.METHOD_ONLINE:
		messages.error(request, 'Only online payments can be confirmed by provider.')
		return redirect('payment_detail', pk=payment.id)

	if request.method != 'POST':
		return redirect('payment_detail', pk=payment.id)

	payment.status = Payment.STATUS_PAID
	payment.paid_at = timezone.now()
	payment.failed_at = None
	payment.failure_reason = None
	payment.save(update_fields=['status', 'paid_at', 'failed_at', 'failure_reason', 'updated_at'])

	logger.info('Payment confirmed for order #%s payment_id=%s transaction_id=%s', payment.order_id, payment.id, payment.transaction_id)
	messages.success(request, f'Payment for order #{payment.order_id} marked as Paid.')
	return redirect('payment_detail', pk=payment.id)


@role_required(['admin'])
def payment_fail(request, pk):
	payment = get_object_or_404(Payment, pk=pk)

	if payment.method != Payment.METHOD_ONLINE:
		messages.error(request, 'Only online payments can be failed by provider.')
		return redirect('payment_detail', pk=payment.id)

	if request.method != 'POST':
		return redirect('payment_detail', pk=payment.id)

	failure_reason = request.POST.get('failure_reason', '').strip() or 'Payment provider reported an unsuccessful transaction.'
	payment.status = Payment.STATUS_FAILED
	payment.failed_at = timezone.now()
	payment.failure_reason = failure_reason
	payment.paid_at = None
	payment.save(update_fields=['status', 'failed_at', 'failure_reason', 'paid_at', 'updated_at'])

	logger.error('Payment failed for order #%s payment_id=%s transaction_id=%s reason=%s', payment.order_id, payment.id, payment.transaction_id, failure_reason)
	messages.error(request, f'Payment for order #{payment.order_id} marked as Failed.')
	return redirect('payment_detail', pk=payment.id)


@role_required(['client'])
def payment_retry(request, pk):
	payment = get_object_or_404(Payment, pk=pk)

	if payment.order.customer_id != request.user.id:
		raise Http404('Payment not found')

	if payment.method != Payment.METHOD_ONLINE:
		messages.error(request, 'Only online payments can be retried.')
		return redirect('payment_detail', pk=payment.id)

	if payment.status != Payment.STATUS_FAILED:
		messages.error(request, 'Only failed payments can be retried.')
		return redirect('payment_detail', pk=payment.id)

	if request.method != 'POST':
		return redirect('payment_detail', pk=payment.id)

	payment.status = Payment.STATUS_PENDING_PAYMENT
	payment.failed_at = None
	payment.failure_reason = None
	payment.paid_at = None
	payment.transaction_id = f"TXN-{payment.order.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
	payment.save(update_fields=['status', 'failed_at', 'failure_reason', 'paid_at', 'transaction_id', 'updated_at'])

	logger.info('Payment retried for order #%s payment_id=%s new_transaction_id=%s', payment.order_id, payment.id, payment.transaction_id)
	messages.success(request, f'Payment for order #{payment.order_id} has been reset for retry. Please try again.')
	return redirect('payment_detail', pk=payment.id)
