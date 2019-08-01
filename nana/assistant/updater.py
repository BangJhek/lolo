import os, time, html, random

from nana import app, setbot, Owner, AdminSettings, USERBOT_VERSION, ASSISTANT_VERSION, log
from __main__ import restart_all
from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton, errors

from git import Repo, exc


OFFICIAL_BRANCH = ('master', 'dev')
REPOSITORY = "https://github.com/AyraHikari/Nana-TgBot"
RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI", "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]

def gen_chlog(repo, diff):
	changelog = ""
	d_form = "%H:%M - %d/%m/%y"
	for cl in repo.iter_commits(diff):
		changelog += f'• [{cl.committed_datetime.strftime(d_form)}]: {cl.summary} <{cl.author}>\n'
	return changelog

def update_changelog(changelog):
	setbot.send_sticker(Owner, random.choice(RANDOM_STICKERS))
	text = "**Update successfully!**\n"
	text += f"🎉 Welcome to Nana Bot v{USERBOT_VERSION} & Assistant v{ASSISTANT_VERSION}\n"
	text += "\n──「 **Update changelogs** 」──\n"
	text += changelog
	setbot.send_message(Owner, text)


def update_checker():
	try:
		repo = Repo()
	except exc.NoSuchPathError as error:
		log.warning(f"Check update failed!\nDirectory {error} is not found!")
		return
	except exc.InvalidGitRepositoryError as error:
		log.warning(f"Check update failed!\nDirectory {error} does not seems to be a git repository")
		return
	except exc.GitCommandError as error:
		log.warning(f"Check update failed!\n{error}")
		return

	brname = repo.active_branch.name
	if brname not in OFFICIAL_BRANCH:
		return

	try:
		repo.create_remote('upstream', REPOSITORY)
	except BaseException:
		pass

	upstream = repo.remote('upstream')
	upstream.fetch(brname)
	changelog = gen_chlog(repo, f'HEAD..upstream/{brname}')

	if not changelog:
		log.info(f'Nana is up-to-date with branch {brname}')
		return

	log.warning(f'New UPDATE available for [{brname}]!')

	text = f"**New UPDATE available for [{brname}]!**\n\n"
	text += f"**CHANGELOG:**\n`{changelog}`"
	button = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Update Now!", callback_data="update_now")]])
	setbot.send_message(Owner, text, reply_markup=button, parse_mode="markdown")

# For callback query button
def dynamic_data_filter(data):
	return Filters.create(
		lambda flt, query: flt.data == query.data,
		data=data  # "data" kwarg is accessed with "flt.data" above
	)

@setbot.on_callback_query(dynamic_data_filter("update_now"))
def update_button(client, query):
	query.message.edit_text("Updating, please wait...")
	try:
		repo = Repo()
	except exc.NoSuchPathError as error:
		log.warning(f"Check update failed!\nDirectory {error} is not found!")
		return
	except exc.InvalidGitRepositoryError as error:
		log.warning(f"Check update failed!\nDirectory {error} does not seems to be a git repository")
		return
	except exc.GitCommandError as error:
		log.warning(f"Check update failed!\n{error}")
		return

	brname = repo.active_branch.name
	if brname not in OFFICIAL_BRANCH:
		return

	try:
		repo.create_remote('upstream', REPOSITORY)
	except BaseException:
		pass

	upstream = repo.remote('upstream')
	upstream.fetch(brname)
	changelog = gen_chlog(repo, f'HEAD..upstream/{brname}')

	try:
		upstream.pull(brname)
		query.message.edit_text('Successfully Updated!\nBot is restarting...')
	except GitCommandError:
		upstream.git.reset('--hard')
		query.message.edit_text('Successfully Updated!\nBot is restarting...')
	update_changelog(changelog)
	restart_all()

update_checker()
