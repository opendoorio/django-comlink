from django.template import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
import datetime
from django.views.decorators.csrf import csrf_exempt

from models import MailingList, IncomingMail
from staff.models import Member

@staff_member_required
def index(request):
	lists = MailingList.objects.all()
	return render_to_response('comlink/index.html', {'lists':lists}, context_instance=RequestContext(request))

@staff_member_required
def list_messages(request, list_id):
	mailing_list = get_object_or_404(MailingList, pk=list_id)
	return render_to_response('comlink/messages.html', {'mailing_list':mailing_list}, context_instance=RequestContext(request))

@staff_member_required
def list_subscribers(request, list_id):
	mailing_list = get_object_or_404(MailingList, pk=list_id)
	not_subscribed = Member.objects.active_members().exclude(user__in=mailing_list.subscribers.all)
	return render_to_response('comlink/subscribers.html', {'mailing_list':mailing_list, 'not_subscribed':not_subscribed}, context_instance=RequestContext(request))

@login_required
def subscribe(request, list_id, username):
	mailing_list = get_object_or_404(MailingList, pk=list_id)
	user = get_object_or_404(User, username=username)
	if request.method == 'POST':
		if request.POST.get('confirm', 'No') == "Yes":
			mailing_list.subscribers.add(user)
		return HttpResponseRedirect(reverse('comlink.views.list_subscribers', args=[list_id]))
	return render_to_response('comlink/subscribe.html', {'member':user.get_profile(), 'mailing_list':mailing_list}, context_instance=RequestContext(request))

@login_required
def unsubscribe(request, list_id, username):
	mailing_list = get_object_or_404(MailingList, pk=list_id)
	user = get_object_or_404(User, username=username)
	if request.method == 'POST':
		if request.POST.get('confirm', 'No') == "Yes":
			mailing_list.subscribers.remove(user)
		return HttpResponseRedirect(reverse('comlink.views.list_subscribers', args=[list_id]))
	return render_to_response('comlink/unsubscribe.html', {'member':user.get_profile(), 'mailing_list':mailing_list}, context_instance=RequestContext(request))

@staff_member_required
def moderator_list(request):
	return render_to_response('comlink/moderator_list.html', {}, context_instance=RequestContext(request))

@staff_member_required
def moderator_inspect(request, id):
	incoming_mail = get_object_or_404(IncomingMail, pk=id)
	return render_to_response('comlink/moderator_inspect.html', {'incoming_mail':incoming_mail}, context_instance=RequestContext(request))

@staff_member_required
def moderator_approve(request, id):
	incoming_mail = get_object_or_404(IncomingMail, pk=id)
	if not request.user in incoming_mail.mailing_list.moderators.all():
		print request.user.get_full_name(), 'tried to moderate an email for %s' % incoming_mail.mailing_list.name
		return HttpResponseRedirect(reverse('comlink.views.moderator_list'))

	if incoming_mail.state != 'moderate':
		print 'Tried to moderate an email which needs no moderation:', incoming_mail, incoming_mail.state
		return HttpResponseRedirect(reverse('comlink.views.moderator_list'))
	print 'accepting'
	incoming_mail.create_outgoing()
	return HttpResponseRedirect(reverse('comlink.views.moderator_list'))

@staff_member_required
def moderator_reject(request, id):
	incoming_mail = get_object_or_404(IncomingMail, pk=id)
	if not request.user in incoming_mail.mailing_list.moderators.all():
		print request.user.get_full_name(), 'tried to moderate an email for %s' % incoming_mail.mailing_list.name
		return HttpResponseRedirect(reverse('comlink.views.moderator_list'))

	if incoming_mail.state != 'moderate':
		print 'Tried to moderate an email which needs no moderation.'
		return HttpResponseRedirect(reverse('comlink.views.moderator_list'))

	print 'rejecting'
	incoming_mail.reject()
	return HttpResponseRedirect(reverse('comlink.views.moderator_list'))

@csrf_exempt
def email_receive(request):
	# determine which mailing list this was for 
	if request.method == 'POST':
		# attachments
		file_names = []
		for key in request.FILES:
			file_names.append(request.FILES[key])
			# TODO: do something real with the files

		msg_timestamp = datetime.datetime.fromtimestamp(int(request.POST.get('timestamp')).strftime('%Y-%m-%d %H:%M:%S'))
		message = {
			'sender': request.POST.get('sender'),
			'recipient': request.POST.get('recipient'),
			'subject': request.POST.get('subject', ''),
			'body': request.POST.get('body-plain', ''),
			'html_body': request.POST.get('stripped-text', ''),
			'file_names': file_names,
			'sent_time': msg_timestamp,
			'headers': request.POST.get('message-headers', '')
		}

		mailing_list = MailingList.object.get(email_address = recipient)

		# add the message to the database
		mailing_list.create_incoming(message)

		# process incoming and outgoing mail
		# TODO we could process messages on a message by message basis since
		# this callback will be hit once per message, but that's for later...
		IncomingMail.objects.process_incoming()
		OutgoingMail.objects.send_outgoing()

	# Returned text is ignored but HTTP status code matters:
	# Mailgun wants to see 2xx, otherwise it will make another attempt in 5 minutes
	return HttpResponse('OK')

# Copyright 2011 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
