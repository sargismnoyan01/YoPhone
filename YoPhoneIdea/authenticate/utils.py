from django.core.mail import EmailMultiAlternatives


def send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=None):
    msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)

    if html_message:
        msg.attach_alternative(html_message, "text/html")  # Attach HTML content

    return msg.send(fail_silently=fail_silently)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
