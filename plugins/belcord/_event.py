from asyncio import create_task as ct,gather as g


client = None


# --- Custom Events ---

_builtin_events = set((
    "on_raw_app_command_permissions_update",
    "on_app_command_completion",
    "on_automod_rule_create",
    "on_automod_rule_update",
    "on_automod_rule_delete",
    "on_automod_action",
    "on_guild_channel_delete",
    "on_guild_channel_create",
    "on_guild_channel_update",
    "on_guild_channel_pins_update",
    "on_private_channel_update",
    "on_private_channel_pins_update",
    "on_typing",
    "on_raw_typing",
    "on_connect",
    "on_disconnect",
    "on_shard_connect",
    "on_shard_connect",
    "on_shard_disconnect",
    "on_error",
    "on_socket_event_type",
    "on_socket_raw_receive",
    "on_socket_raw_send",
    "on_entitlement_create",
    "on_entitlement_update",
    "on_entitlement_delete",
    "on_ready",
    "on_startup",  # Added by Belcord
    "on_closing",  # Added by Belcord
    "on_resumed",
    "on_shard_ready",
    "on_shard_resumed",
    "on_guild_available",
    "on_guild_unavailable",
    "on_guild_join",
    "on_guild_remove",
    "on_guild_update",
    "on_guild_emojis_update",
    "on_guild_stickers_update",
    "on_audit_log_entry_create",
    "on_invite_create",
    "on_invite_delete",
    "on_integration_create",
    "on_integration_update",
    "on_guild_integrations_update",
    "on_webhooks_update",
    "on_raw_integration_delete",
    "on_interaction",
    "on_member_join",
    "on_member_remove",
    "on_raw_member_remove",
    "on_member_update",
    "on_user_update",
    "on_member_ban",
    "on_member_unban",
    "on_presence_update",
    "on_raw_presence_update",
    "on_message",
    "on_message_edit",
    "on_message_delete",
    "on_bulk_message_delete",
    "on_raw_message_edit",
    "on_raw_message_delete",
    "on_raw_bulk_message_delete",
    "on_poll_vote_add",
    "on_poll_vote_remove",
    "on_raw_poll_vote_add",
    "on_raw_poll_vote_remove",
    "on_reaction_add",
    "on_reaction_remove",
    "on_reaction_clear",
    "on_reaction_clear_emoji",
    "on_raw_reaction_add",
    "on_raw_reaction_remove",
    "on_raw_reaction_clear",
    "on_raw_reaction_clear_emoji",
    "on_guild_role_create",
    "on_guild_role_delete",
    "on_guild_role_update",
    "on_scheduled_event_create",
    "on_scheduled_event_delete",
    "on_scheduled_event_update",
    "on_scheduled_event_user_add",
    "on_scheduled_event_user_remove",
    "on_soundboard_sound_create",
    "on_soundboard_sound_delete",
    "on_soundboard_sound_update",
    "on_stage_instance_create",
    "on_stage_instance_delete",
    "on_stage_instance_update",
    "on_subscription_create",
    "on_subscription_update",
    "on_subscription_delete",
    "on_thread_create",
    "on_thread_join",
    "on_thread_update",
    "on_thread_remove",
    "on_thread_delete",
    "on_raw_thread_update",
    "on_raw_thread_delete",
    "on_thread_member_join",
    "on_thread_member_remove",
    "on_raw_thread_member_remove",
    "on_voice_state_update",
    "on_voice_channel_effect"
))


async def trigger_event(event_name: str, *args, **kwargs):
    """Trigger a custom client event."""
    event = f"_{event_name}"

    if (funcs := getattr(client.event, event, None)) is None:
        raise RuntimeError(f"Event '{event_name}' does not exist")

    for f in funcs:
        ct(t(*args, **kwargs))


def create_event(event_name: str):
    """Create a custom client event."""
    event = f"_{event_name}"

    if getattr(client.event, event, None) is not None:
        warn(f"Event '{event_name}' already exists", RuntimeWarning)
    else:
        setattr(client.event, event, [])


def remove_event(event_name: str):
    """Delete a custom client event."""
    if event_name in _builtin_events:
        raise RuntimeError(f"Cannot remove built-in event '{event_name}'")

    event = f"_{event_name}"

    try:
        delattr(client.event, event)
        return
    except TypeError:
        pass

    raise RuntimeError(f"Event '{event_name}' does not exist")


# --- some random light-weight event handler down here 👇 ---

class EventHandler:
	def __init__(self):
		self._on_raw_app_command_permissions_update=[]
		self._on_app_command_completion=[]
		self._on_automod_rule_create=[]
		self._on_automod_rule_update=[]
		self._on_automod_rule_delete=[]
		self._on_automod_action=[]
		self._on_guild_channel_delete=[]
		self._on_guild_channel_create=[]
		self._on_guild_channel_update=[]
		self._on_guild_channel_pins_update=[]
		self._on_private_channel_update=[]
		self._on_private_channel_pins_update=[]
		self._on_typing=[]
		self._on_raw_typing=[]
		self._on_connect=[]
		self._on_disconnect=[]
		self._on_shard_connect=[]
		self._on_shard_connect=[]
		self._on_shard_disconnect=[]
		self._on_error=[]
		self._on_socket_event_type=[]
		self._on_socket_raw_receive=[]
		self._on_socket_raw_send=[]
		self._on_entitlement_create=[]
		self._on_entitlement_update=[]
		self._on_entitlement_delete=[]
		self._on_ready=[]
		self._on_startup=[]  # Added by Belcord
		self._on_closing=[]  # Added by Belcord
		self._on_resumed=[]
		self._on_shard_ready=[]
		self._on_shard_resumed=[]
		self._on_guild_available=[]
		self._on_guild_unavailable=[]
		self._on_guild_join=[]
		self._on_guild_remove=[]
		self._on_guild_update=[]
		self._on_guild_emojis_update=[]
		self._on_guild_stickers_update=[]
		self._on_audit_log_entry_create=[]
		self._on_invite_create=[]
		self._on_invite_delete=[]
		self._on_integration_create=[]
		self._on_integration_update=[]
		self._on_guild_integrations_update=[]
		self._on_webhooks_update=[]
		self._on_raw_integration_delete=[]
		self._on_interaction=[]
		self._on_member_join=[]
		self._on_member_remove=[]
		self._on_raw_member_remove=[]
		self._on_member_update=[]
		self._on_user_update=[]
		self._on_member_ban=[]
		self._on_member_unban=[]
		self._on_presence_update=[]
		self._on_raw_presence_update=[]
		self._on_message=[]
		self._on_message_edit=[]
		self._on_message_delete=[]
		self._on_bulk_message_delete=[]
		self._on_raw_message_edit=[]
		self._on_raw_message_delete=[]
		self._on_raw_bulk_message_delete=[]
		self._on_poll_vote_add=[]
		self._on_poll_vote_remove=[]
		self._on_raw_poll_vote_add=[]
		self._on_raw_poll_vote_remove=[]
		self._on_reaction_add=[]
		self._on_reaction_remove=[]
		self._on_reaction_clear=[]
		self._on_reaction_clear_emoji=[]
		self._on_raw_reaction_add=[]
		self._on_raw_reaction_remove=[]
		self._on_raw_reaction_clear=[]
		self._on_raw_reaction_clear_emoji=[]
		self._on_guild_role_create=[]
		self._on_guild_role_delete=[]
		self._on_guild_role_update=[]
		self._on_scheduled_event_create=[]
		self._on_scheduled_event_delete=[]
		self._on_scheduled_event_update=[]
		self._on_scheduled_event_user_add=[]
		self._on_scheduled_event_user_remove=[]
		self._on_soundboard_sound_create=[]
		self._on_soundboard_sound_delete=[]
		self._on_soundboard_sound_update=[]
		self._on_stage_instance_create=[]
		self._on_stage_instance_delete=[]
		self._on_stage_instance_update=[]
		self._on_subscription_create=[]
		self._on_subscription_update=[]
		self._on_subscription_delete=[]
		self._on_thread_create=[]
		self._on_thread_join=[]
		self._on_thread_update=[]
		self._on_thread_remove=[]
		self._on_thread_delete=[]
		self._on_raw_thread_update=[]
		self._on_raw_thread_delete=[]
		self._on_thread_member_join=[]
		self._on_thread_member_remove=[]
		self._on_raw_thread_member_remove=[]
		self._on_voice_state_update=[]
		self._on_voice_channel_effect=[]

	def __call__(self,func):
		try:
			self.__dict__[f"_{func.__name__}"].append(func)
			return func
		except KeyError:pass
		raise ValueError(f"Event '{func.__name__}' does not exist")

def configure(client):
	eh = EventHandler()
	async def close():
		await g(*eh._on_closing)
		for e in eh.__dict__.values():
			e.clear()
		await client._close()
		client.running = False
	@client.event
	async def on_raw_app_command_permissions_update(payload):
		for f in eh._on_raw_app_command_permissions_update:ct(f(payload))
	@client.event
	async def on_app_command_completion(interaction,command):
		for f in eh._on_app_command_completion:ct(f(interaction,command))
	@client.event
	async def on_automod_rule_create(rule):
		for f in eh._on_automod_rule_create:ct(f(rule))
	@client.event
	async def on_automod_rule_update(rule):
		for f in eh._on_automod_rule_update:ct(f(rule))
	@client.event
	async def on_automod_rule_delete(rule):
		for f in eh._on_automod_rule_delete:ct(f(rule))
	@client.event
	async def on_automod_action(execution):
		for f in eh._on_automod_action:ct(f(execution))
	@client.event
	async def on_guild_channel_delete(channel):
		for f in eh._on_guild_channel_delete:ct(f(channel))
	@client.event
	async def on_guild_channel_create(channel):
		for f in eh._on_guild_channel_create:ct(f(channel))
	@client.event
	async def on_guild_channel_update(before,after):
		for f in eh._on_guild_channel_update:ct(f(before,after))
	@client.event
	async def on_guild_channel_pins_update(channel,last_pin):
		for f in eh._on_guild_channel_pins_update:ct(f(channel,last_pin))
	@client.event
	async def on_private_channel_update(before,after):
		for f in eh._on_private_channel_update:ct(f(before,after))
	@client.event
	async def on_private_channel_pins_update(channel,last_pin):
		for f in eh._on_private_channel_pins_update:ct(f(channel,last_pin))
	@client.event
	async def on_typing(channel,user,when):
		for f in eh._on_typing:ct(f(channel,user,when))
	@client.event
	async def on_raw_typing(payload):
		for f in eh._on_raw_typing:ct(f(payload))
	@client.event
	async def on_connect():
		for f in eh._on_connect:ct(f())
	@client.event
	async def on_disconnect():
		for f in eh._on_disconnect:ct(f())
	@client.event
	async def on_shard_connect(shard_id):
		for f in eh._on_shard_connect:ct(f(shard_id))
	@client.event
	async def on_shard_connect(shard_id):
		for f in eh._on_shard_connect:ct(f(shard_id))
	@client.event
	async def on_shard_disconnect(shard_id):
		for f in eh._on_shard_disconnect:ct(f(shard_id))
	@client.event
	async def on_error(event,*args,**kwargs):
		for f in eh._on_error:ct(f(event,*args,**kwargs))
	@client.event
	async def on_socket_event_type(event_type):
		for f in eh._on_socket_event_type:ct(f(event_type))
	@client.event
	async def on_socket_raw_receive(msg):
		for f in eh._on_socket_raw_receive:ct(f(msg))
	@client.event
	async def on_socket_raw_send(payload):
		for f in eh._on_socket_raw_send:ct(f(payload))
	@client.event
	async def on_entitlement_create(entitlement):
		for f in eh._on_entitlement_create:ct(f(entitlement))
	@client.event
	async def on_entitlement_update(entitlement):
		for f in eh._on_entitlement_update:ct(f(entitlement))
	@client.event
	async def on_entitlement_delete(entitlement):
		for f in eh._on_entitlement_delete:ct(f(entitlement))
	@client.event
	async def on_ready():
		client.running=True
		if not client._started:
			client._started=True
			for f in eh._on_startup:ct(f())
		for f in eh._on_ready:ct(f())
	@client.event
	async def on_resumed():
		for f in eh._on_resumed:ct(f())
	@client.event
	async def on_shard_ready(shard_id):
		for f in eh._on_shard_ready:ct(f(shard_id))
	@client.event
	async def on_shard_resumed(shard_id):
		for f in eh._on_shard_resumed:ct(f(shard_id))
	@client.event
	async def on_guild_available(guild):
		for f in eh._on_guild_available:ct(f(guild))
	@client.event
	async def on_guild_unavailable(guild):
		for f in eh._on_guild_unavailable:ct(f(guild))
	@client.event
	async def on_guild_join(guild):
		for f in eh._on_guild_join:ct(f(guild))
	@client.event
	async def on_guild_remove(guild):
		for f in eh._on_guild_remove:ct(f(guild))
	@client.event
	async def on_guild_update(before,after):
		for f in eh._on_guild_update:ct(f(before,after))
	@client.event
	async def on_guild_emojis_update(guild,before,after):
		for f in eh._on_guild_emojis_update:ct(f(guild,before,after))
	@client.event
	async def on_guild_stickers_update(guild,before,after):
		for f in eh._on_guild_stickers_update:ct(f(guild,before,after))
	@client.event
	async def on_audit_log_entry_create(entry):
		for f in eh._on_audit_log_entry_create:ct(f(entry))
	@client.event
	async def on_invite_create(invite):
		for f in eh._on_invite_create:ct(f(invite))
	@client.event
	async def on_invite_delete(invite):
		for f in eh._on_invite_delete:ct(f(invite))
	@client.event
	async def on_integration_create(integration):
		for f in eh._on_integration_create:ct(f(integration))
	@client.event
	async def on_integration_update(integration):
		for f in eh._on_integration_update:ct(f(integration))
	@client.event
	async def on_guild_integrations_update(guild):
		for f in eh._on_guild_integrations_update:ct(f(guild))
	@client.event
	async def on_webhooks_update(channel):
		for f in eh._on_webhooks_update:ct(f(channel))
	@client.event
	async def on_raw_integration_delete(payload):
		for f in eh._on_raw_integration_delete:ct(f(payload))
	@client.event
	async def on_interaction(interaction):
		for f in eh._on_interaction:ct(f(interaction))
	@client.event
	async def on_member_join(member):
		for f in eh._on_member_join:ct(f(member))
	@client.event
	async def on_member_remove(member):
		for f in eh._on_member_remove:ct(f(member))
	@client.event
	async def on_raw_member_remove(payload):
		for f in eh._on_raw_member_remove:ct(f(payload))
	@client.event
	async def on_member_update(before,after):
		for f in eh._on_member_update:ct(f(before,after))
	@client.event
	async def on_user_update(before,after):
		for f in eh._on_user_update:ct(f(before,after))
	@client.event
	async def on_member_ban(guild,user):
		for f in eh._on_member_ban:ct(f(guild,user))
	@client.event
	async def on_member_unban(guild,user):
		for f in eh._on_member_unban:ct(f(guild,user))
	@client.event
	async def on_presence_update(before,after):
		for f in eh._on_presence_update:ct(f(before,after))
	@client.event
	async def on_raw_presence_update(payload):
		for f in eh._on_raw_presence_update:ct(f(payload))
	@client.event
	async def on_message(message):
		for f in eh._on_message:ct(f(message))
	@client.event
	async def on_message_edit(before,after):
		for f in eh._on_message_edit:ct(f(before,after))
	@client.event
	async def on_message_delete(message):
		for f in eh._on_message_delete:ct(f(message))
	@client.event
	async def on_bulk_message_delete(messages):
		for f in eh._on_bulk_message_delete:ct(f(messages))
	@client.event
	async def on_raw_message_edit(payload):
		for f in eh._on_raw_message_edit:ct(f(payload))
	@client.event
	async def on_raw_message_delete(payload):
		for f in eh._on_raw_message_delete:ct(f(payload))
	@client.event
	async def on_raw_bulk_message_delete(payload):
		for f in eh._on_raw_bulk_message_delete:ct(f(payload))
	@client.event
	async def on_poll_vote_add(user,answer):
		for f in eh._on_poll_vote_add:ct(f(user,answer))
	@client.event
	async def on_poll_vote_remove(user,answer):
		for f in eh._on_poll_vote_remove:ct(f(user,answer))
	@client.event
	async def on_raw_poll_vote_add(payload):
		for f in eh._on_raw_poll_vote_add:ct(f(payload))
	@client.event
	async def on_raw_poll_vote_remove(payload):
		for f in eh._on_raw_poll_vote_remove:ct(f(payload))
	@client.event
	async def on_reaction_add(reaction,user):
		for f in eh._on_reaction_add:ct(f(reaction,user))
	@client.event
	async def on_reaction_remove(reaction,user):
		for f in eh._on_reaction_remove:ct(f(reaction,user))
	@client.event
	async def on_reaction_clear(message,reactions):
		for f in eh._on_reaction_clear:ct(f(message,reactions))
	@client.event
	async def on_reaction_clear_emoji(reaction):
		for f in eh._on_reaction_clear_emoji:ct(f(reaction))
	@client.event
	async def on_raw_reaction_add(payload):
		for f in eh._on_raw_reaction_add:ct(f(payload))
	@client.event
	async def on_raw_reaction_remove(payload):
		for f in eh._on_raw_reaction_remove:ct(f(payload))
	@client.event
	async def on_raw_reaction_clear(payload):
		for f in eh._on_raw_reaction_clear:ct(f(payload))
	@client.event
	async def on_raw_reaction_clear_emoji(payload):
		for f in eh._on_raw_reaction_clear_emoji:ct(f(payload))
	@client.event
	async def on_guild_role_create(role):
		for f in eh._on_guild_role_create:ct(f(role))
	@client.event
	async def on_guild_role_delete(role):
		for f in eh._on_guild_role_delete:ct(f(role))
	@client.event
	async def on_guild_role_update(before,after):
		for f in eh._on_guild_role_update:ct(f(before,after))
	@client.event
	async def on_scheduled_event_create(event):
		for f in eh._on_scheduled_event_create:ct(f(event))
	@client.event
	async def on_scheduled_event_delete(event):
		for f in eh._on_scheduled_event_delete:ct(f(event))
	@client.event
	async def on_scheduled_event_update(before,after):
		for f in eh._on_scheduled_event_update:ct(f(before,after))
	@client.event
	async def on_scheduled_event_user_add(event,user):
		for f in eh._on_scheduled_event_user_add:ct(f(event,user))
	@client.event
	async def on_scheduled_event_user_remove(event,user):
		for f in eh._on_scheduled_event_user_remove:ct(f(event,user))
	@client.event
	async def on_soundboard_sound_create(sound):
		for f in eh._on_soundboard_sound_create:ct(f(sound))
	@client.event
	async def on_soundboard_sound_delete(sound):
		for f in eh._on_soundboard_sound_delete:ct(f(sound))
	@client.event
	async def on_soundboard_sound_update(before,after):
		for f in eh._on_soundboard_sound_update:ct(f(before,after))
	@client.event
	async def on_stage_instance_create(stage_instance):
		for f in eh._on_stage_instance_create:ct(f(stage_instance))
	@client.event
	async def on_stage_instance_delete(stage_instance):
		for f in eh._on_stage_instance_delete:ct(f(stage_instance))
	@client.event
	async def on_stage_instance_update(before,after):
		for f in eh._on_stage_instance_update:ct(f(before,after))
	@client.event
	async def on_subscription_create(subscription):
		for f in eh._on_subscription_create:ct(f(subscription))
	@client.event
	async def on_subscription_update(subscription):
		for f in eh._on_subscription_update:ct(f(subscription))
	@client.event
	async def on_subscription_delete(subscription):
		for f in eh._on_subscription_delete:ct(f(subscription))
	@client.event
	async def on_thread_create(thread):
		for f in eh._on_thread_create:ct(f(thread))
	@client.event
	async def on_thread_join(thread):
		for f in eh._on_thread_join:ct(f(thread))
	@client.event
	async def on_thread_update(before,after):
		for f in eh._on_thread_update:ct(f(before,after))
	@client.event
	async def on_thread_remove(thread):
		for f in eh._on_thread_remove:ct(f(thread))
	@client.event
	async def on_thread_delete(thread):
		for f in eh._on_thread_delete:ct(f(thread))
	@client.event
	async def on_raw_thread_update(payload):
		for f in eh._on_raw_thread_update:ct(f(payload))
	@client.event
	async def on_raw_thread_delete(payload):
		for f in eh._on_raw_thread_delete:ct(f(payload))
	@client.event
	async def on_thread_member_join(member):
		for f in eh._on_thread_member_join:ct(f(member))
	@client.event
	async def on_thread_member_remove(member):
		for f in eh._on_thread_member_remove:ct(f(member))
	@client.event
	async def on_raw_thread_member_remove(payload):
		for f in eh._on_raw_thread_member_remove:ct(f(payload))
	@client.event
	async def on_voice_state_update(member,before,after):
		for f in eh._on_voice_state_update:ct(f(member,before,after))
	@client.event
	async def on_voice_channel_effect(effect):
		for f in eh._on_voice_channel_effect:ct(f(effect))
	client.running=False
	client._started=False
	client._event=client.event
	client.event=eh
	client._close=client.close
	client.close=close
	globals()["client"]=client
