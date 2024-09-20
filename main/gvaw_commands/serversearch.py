import utility
import logging

logger = logging.getLogger(__name__)


async def server_searchLogic(
    ctx, discordEmbed, firestore, db, author, channelId, guildId, serverTitle
):

    channelList = utility.retrieveDb_data(db, option="channel-list", title=guildId)
    channelVerify = await utility.checkChannel(
        db, firestore, channelList, channelId, guildId
    )
    usageMessage = "`!serversearch server name`\n------"
    embed = discordEmbed(
        title="GvAW Server Search",
        description="Search for ArmA 3 server IP address by server name",
        color=0xE74C3C,
    )

    embed.set_thumbnail(url=utility.gvawLogo_url)
    embed.add_field(name="__Usage__", value=usageMessage)

    if channelVerify:

        try:
            serverData = await utility.getData(
                f"https://api.battlemetrics.com/servers",
                params={"filter[search]": serverTitle, "filter[game]": "arma3"},
            )
        except TypeError:
            return await ctx.send(embed=embed)

        if serverData is None:
            logger.error("Battlemetrics API response returns None")
            return await ctx.send(f"An error has occured, please contact {author}")

        else:
            if not serverData["data"]:
                embed.add_field(
                    name="__Search Result__", value="No server found.\n------"
                )
                return await ctx.send(embed=embed)

            searchResult = await utility.search_resultFormat(serverData)
            embed.add_field(name="__Search Result__", value=f"{searchResult}\n------")
            await ctx.send(embed=embed)

            if serverData["links"]:
                while True:

                    def check(msg):
                        return msg.author == ctx.message.author

                    try:
                        link = serverData["links"]["next"]
                    except KeyError:
                        break

                    await ctx.send(
                        "Send `!next` to browse more or send `!quit` to quit browsing."
                    )
                    msg = await ctx.bot.wait_for("message", check=check)

                    if msg.content == "!quit":
                        break

                    elif msg.content == "!next":
                        serverData = await utility.getData(link, params=None)
                        searchResult = await utility.search_resultFormat(serverData)
                        embed.set_field_at(
                            1, name="__Search Result__", value=f"{searchResult}\n------"
                        )
                        await ctx.send(embed=embed)

            return await ctx.send("Search completed.")

    else:
        return await ctx.send(
            "`This channel is not authorized. Use !channelconfig to authorize channels.`"
        )
