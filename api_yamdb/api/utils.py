import uuid

from django.core.mail import send_mail


def send_confirmation_code(user):
    """Sending confirmation code to user email."""
    confirmation_code = uuid.uuid5(uuid.NAMESPACE_OID, user.__str__())
    subject = 'Код подтверждения'
    message = (f'username: {user.username}\n'
               f'confirmation_code: {confirmation_code}')
    return send_mail(subject, message, None, (user.email, ))
