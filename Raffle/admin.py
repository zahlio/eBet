from django.contrib import admin
from django.shortcuts import get_object_or_404
from Raffle.models import *
from django.contrib import messages

# Register your models here.


class RaffleAdmin(admin.ModelAdmin):

    def end(self, request, queryset):
        raffles = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        for raffle_id in raffles:
            raffle = get_object_or_404(Raffle, id=raffle_id)
            if raffle.winner is None:
                raffle.end()
                messages.success(request, "#" + str(raffle.id) + " has a winner: " + str(raffle.winner.email))
            else:
                messages.warning(request, "#" + str(raffle.id) + " already has a winner: " + str(raffle.winner.email))

    end.short_description = "End raffle and pick winner"
    actions = [end]


admin.site.register(Price)
admin.site.register(Raffle, RaffleAdmin)
admin.site.register(RaffleEntry)