from core.models import MEMBER_MODEL, PARTY_MODEL
from django.utils.translation import ugettext_lazy as _

from modeltranslation.translator import register, TranslationOptions


@register(PARTY_MODEL)
class PartyModelTranslatorOptions(TranslationOptions):
    fields = ('name',)
    fallback_values = _('-- sorry, no translation provided --')


@register(MEMBER_MODEL)
class MemberModelTranslatorOptions(TranslationOptions):
    fields = ('name',)
    fallback_values = _('-- sorry, no translation provided --')
