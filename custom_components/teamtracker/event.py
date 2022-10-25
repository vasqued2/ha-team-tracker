import arrow
import logging

from .const import (
    CONF_CONFERENCE_ID,
    CONF_LEAGUE_ID,
    CONF_LEAGUE_PATH,
    CONF_SPORT_PATH,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    COORDINATOR,
    DEFAULT_CONFERENCE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_LEAGUE,
    DEFAULT_LOGO,
    DEFAULT_LEAGUE_PATH,
    DEFAULT_PROB,
    DEFAULT_SPORT_PATH,
    DOMAIN,
    ISSUE_URL,
    LEAGUE_LIST,
    PLATFORMS,
    URL_HEAD,
    URL_TAIL,
    USER_AGENT,
    VERSION,
)


_LOGGER = logging.getLogger(__name__)

async def async_process_event(sensor_name, data, sport_path, league_id, DEFAULT_LOGO, team_id, lang) -> dict:
    values = {} 

    values = await async_clear_states2()

    search_key = team_id
    sport = sport_path
    
    values["sport"] = sport_path
    values["league"] = league_id
    values["team_abbr"] = team_id
    values["state"] = 'NOT_FOUND'
    values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
    values["private_fast_refresh"] = False


    found_competitor = False
    if data is not None:
        try:
            values["league_logo"] = data["leagues"][0]["logos"][0]["href"]
        except:
            values["league_logo"] = DEFAULT_LOGO

        for event in data["events"]:
            _LOGGER.debug("%s: Looking at this event: %s", sensor_name, event["shortName"])
            try:
                comp_index = 0
                for competition in event["competitions"]:
#                    _LOGGER.debug("%s: Looking at this competition: %s", sensor_name, competition["id"])
                    index = 0
                    for competitor in competition["competitors"]:
                        if competitor["type"] == "team":
                            _LOGGER.debug("%s: Competitor: %s", sensor_name, competitor["team"]["displayName"])
                        if competitor["type"] == "athlete":
#                            _LOGGER.debug("%s: Searching for %s in %s", sensor_name, search_key, competitor["athlete"]["displayName"].upper())
                            if search_key in competitor["athlete"]["displayName"].upper():
#                                _LOGGER.debug("%s: Competitor Found.  Searching for sport: %s", sensor_name, sport)
                                if sport in ["golf", "mma", "racing", "tennis"]:
                                    _LOGGER.debug("%s: Sport Found.  Assigning values for competitor: %s", sensor_name, competitor["athlete"]["displayName"])
                                    try:
                                        values.update(await set_golf_values(values, event, competition, competitor, lang, index, comp_index, sensor_name))
                                        _LOGGER.debug("%s: values[] %s", sensor_name, values)
                                    except:
                                        _LOGGER.warn("%s: exception w/ function call", sensor_name)
                                    _LOGGER.debug("%s: values[] %s %s", sensor_name, type(values), values)
                                    if values["state"] == "IN":
                                        break;
                        index = index + 1
                        if values["state"] == "IN":
                            break;
                    if values["state"] == "IN":
                        break;
                    comp_index = comp_index + 1
                try:
                    if values["state"] == "POST" and event["status"]["type"]["state"].upper() == "IN":
                        break;
                except:
                    values["state"] = values["state"]
                if values["state"] == "IN":
                    break;
            except:
                _LOGGER.debug("%s: No competitions listed for this event: %s", sensor_name, event["shortName"])

    return values



async def async_clear_states2() -> dict:
    """Clear all state attributes"""
    new_values = {}

    # Reset values
    new_values = {
        "sport": None,
        "league": None,
        "league_logo": None,
        "team_abbr": None,
        "opponent_abbr": None,

        "date": None,
        "kickoff_in": None,
        "venue": None,
        "location": None,
        "tv_network": None,
        "odds": None,
        "overunder": None,

        "team_name": None,
        "team_id": None,
        "team_record": None,
        "team_rank": None,
        "team_homeaway": None,
        "team_logo": None,
        "team_colors": None,
        "team_score": None,
        "team_win_probability": None,
        "team_timeouts": None,

        "opponent_name": None,
        "opponent_id": None,
        "opponent_record": None,
        "opponent_rank": None,
        "opponent_homeaway": None,
        "opponent_logo": None,
        "opponent_colors": None,
        "opponent_score": None,
        "opponent_win_probability": None,
        "opponent_timeouts": None,

        "quarter": None,
        "clock": None,
        "possession": None,
        "last_play": None,
        "down_distance_text": None,

        "outs": None,
        "balls": None,
        "strikes": None,
        "on_first": None,
        "on_second": None,
        "on_third": None,

        "team_shots_on_target": None,
        "team_total_shots": None,
        "opponent_shots_on_target": None,
        "opponent_total_shots": None,

        "team_sets_won": None,
        "opponent_sets_won": None,

        "last_update": None,
        "api_message": None,
        
        "private_fast_refresh": False,
    }


    return new_values


async def set_golf_values(old_values, event, competition, competitor, lang, index, comp_index, sensor_name) -> dict:
    new_values = {}
#    new_values["team_colors"] = ["#FFFFFF", "#000000"]
#    new_values["opponent_colors"] = ["#FFFFFF", "#000000"]

    _LOGGER.debug("%s: set_golf_values() 1: %s", sensor_name, sensor_name)

    if index == 0:
        oppo_index = 1
    else:
        oppo_index = 0

    new_values["key"] = "value"

    new_values["sport"] = old_values["sport"]
    new_values["league"] = old_values["league"]
    new_values["team_abbr"] = old_values["team_abbr"]
    new_values["opponent_abbr"] = None

    try:
        new_values["state"] = competition["status"]["type"]["state"].upper()
    except:
        new_values["state"] = event["status"]["type"]["state"].upper()

    try:
        new_values["date"] = competition["date"]
    except:
        new_values["date"] = event["date"]
    new_values["kickoff_in"] = arrow.get(new_values["date"]).humanize(locale=lang)

    try:
        new_values["venue"] = competition["venue"]["fullName"]
    except:
        new_values["venue"] = None

    try:
        new_values["location"] = "%s, %s" % (competition["venue"]["address"]["city"], competition["venue"]["address"]["state"])
    except:
        try:
            new_values["location"] = competition["venue"]["address"]["city"]
        except:
            new_values["location"] = None

    try:
        new_values["tv_network"] = competition["broadcasts"][0]["names"][0]
    except:
        new_values["tv_network"] = None

    try:
        new_values["odds"] = competition["odds"][0]["details"]
    except:
        new_values["odds"] = None

    try:
        new_values["overunder"] = competition["odds"][0]["overUnder"]
    except:
        new_values["overunder"] = None

    try:
        new_values["quarter"] = competition["status"]["period"]
    except:
        new_values["quarter"] = None

    try:
        new_values["clock"] = competition["status"]["type"]["shortDetail"]
    except:
        try:
            new_values["clock"] = event["status"]["type"]["shortDetail"]
        except:
            new_values["clock"] = None

    _LOGGER.debug("%s: set_golf_values() 2: %s", sensor_name, sensor_name)

#    new_values["team_abbr"] = competitor["team"]["abbreviation"]
    new_values["team_id"] = competitor["id"]
    new_values["opponent_id"] = competition["competitors"][oppo_index]["id"]

    new_values["team_name"] = competitor["athlete"]["displayName"]
    new_values["opponent_name"] = competition["competitors"][oppo_index]["athlete"]["displayName"]
    
    try:
        new_values["team_record"] = competitor["records"][0]["summary"]
    except:
        new_values["team_record"] = None
    try:
        new_values["opponent_record"] = competition["competitors"][oppo_index]["records"][0]["summary"]
    except:
        new_values["opponent_record"] = None

    try:
        new_values["team_logo"] = competitor["athlete"]["flag"]["href"]
    except:
        new_values["team_logo"] = DEFAULT_LOGO
    try:
        new_values["opponent_logo"] = competition["competitors"][oppo_index]["athlete"]["flag"]["href"]
    except:
        new_values["opponent_logo"] = DEFAULT_LOGO

    try:
        new_values["team_score"] = competitor["score"]
    except:
        new_values["team_score"] = None
    try:
        new_values["opponent_score"] = competition["competitors"][oppo_index]["score"]
    except:
        new_values["opponent_score"] = None

    try:
        if (competitor["curatedRank"]["current"] != 99):
            new_values["team_rank"] = competitor["curatedRank"]["current"] 
    except:
        new_values["team_rank"] = None
    try:
        if (competition["competitors"][oppo_index]["curatedRank"]["current"] != 99):
            new_values["opponent_rank"] = competition["competitors"][oppo_index]["curatedRank"]["current"] 
    except:
        new_values["opponent_rank"] = None

    _LOGGER.debug("%s: set_golf_values() 3: %s", sensor_name, sensor_name)

    if new_values["state"] == "IN":
        _LOGGER.debug("%s: Event in progress, setting refresh rate to 5 seconds.", sensor_name)
        new_values["private_fast_refresh"] = True

    _LOGGER.debug("%s: set_golf_values() 3.1: %s", sensor_name, sensor_name)

    if new_values["state"] == 'PRE' and (abs((arrow.get(new_values["date"])-arrow.now()).total_seconds()) < 1200):
        _LOGGER.debug("%s: Event is within 20 minutes, setting refresh rate to 5 seconds.", sensor_name)
        new_values["private_fast_refresh"] = True

    _LOGGER.debug("%s: set_golf_values() 3.2: %s", sensor_name, sensor_name)

    if (new_values["sport"] == "golf"):
        try:
            new_values["venue"] = event["shortName"]
        except:
            new_values["venue"] = None

        new_values["team_rank"] = index + 1
        new_values["opponent_rank"] = oppo_index + 1

        new_values["team_rank"] = await get_golf_position(competition, index)
        new_values["opponent_rank"] = await get_golf_position(competition, oppo_index)

        round = new_values["quarter"] - 1
        try:
            new_values["team_total_shots"] = competitor["linescores"][round]["value"]
        except:
            new_values["team_total_shots"] = 0
        try:
            new_values["team_shots_on_target"] = len(competitor["linescores"][round]["linescores"])
        except:
            new_values["team_shots_on_target"] = 0

        try:
            new_values["opponent_total_shots"] = competition["competitors"][oppo_index]["linescores"][round]["value"]
        except:
            new_values["opponent_total_shots"] = 0
        try:
            new_values["opponent_shots_on_target"] = len(competition["competitors"][oppo_index]["linescores"][round]["linescores"])
        except:
            new_values["opponent_shots_on_target"] = 0

        new_values["last_play"] = "LEADERBOARD: "
        for x in range (0, 10):
            try:
                p = await get_golf_position(competition, x)
                new_values["last_play"] = new_values["last_play"] + p + ". "
                new_values["last_play"] = new_values["last_play"] + competition["competitors"][x]["athlete"]["shortName"]
                new_values["last_play"] = new_values["last_play"] + " (" + str(competition["competitors"][x]["score"]) + "),   "
            except:
                new_values["last_play"] = new_values["last_play"]

    if (new_values["sport"] == "tennis"):
        _LOGGER.debug("%s: set_golf_values() 4: %s", sensor_name, sensor_name)

        team_index = index

        try:
            new_values["venue"] = event["shortName"]
        except:
            new_values["venue"] = None

        try:
            remaining_games = len(event["competitions"]) - comp_index;
            _LOGGER.debug("%s: set_golf_values() 4.1: %s %s %s", sensor_name, remaining_games, len(event["competitions"]), comp_index)

            new_values["odds"] = 1<<remaining_games.bit_length() # Game is in the round of X
        except:
            new_values["odds"] = None

        try:
            new_values["team_rank"] = competitor["tournamentSeed"]
        except:
            new_values["team_rank"] = None
        try:
            new_values["opponent_rank"] = competition["competitors"][oppo_index]["tournamentSeed"]
        except:
            new_values["opponent_rank"] = None

        try:
            new_values["clock"] = competition["status"]["type"]["detail"]
        except:
            try:
                new_values["clock"] = event["status"]["type"]["detail"]
            except:
                new_values["clock"] = None

        _LOGGER.debug("%s: set_golf_values() 5: %s", sensor_name, sensor_name)

        new_values["team_sets_won"] = new_values["team_score"]
        new_values["opponent_sets_won"] = new_values["opponent_score"]

        try:
            new_values["team_score"] = competitor["linescores"][-1]["value"]
        except:
            new_values["team_score"] = None
        try:
            new_values["opponent_score"] = competition["competitors"][oppo_index]["linescores"][-1]["value"]
        except:
            new_values["opponent_score"] = None
        try:
            new_values["team_shots_on_target"] = competitor["linescores"][-1]["tiebreak"]
        except:
            new_values["team_shots_on_target"] = None
        try:
            new_values["opponent_shots_on_target"] = competition["competitors"][oppo_index]["linescores"][-1]["tiebreak"]
        except:
            new_values["opponent_shots_on_target"] = None

        _LOGGER.debug("%s: set_golf_values() 6: %s", sensor_name, sensor_name)

        if new_values["state"] == "POST":
            new_values["team_score"] = 0
            new_values["opponent_score"] = 0
            _LOGGER.debug("%s: set_golf_values() 7: %s", sensor_name, sensor_name)

            for x in range (0, len(competitor["linescores"])):
                _LOGGER.debug("%s: set_golf_values() 8: %s", sensor_name, len(competitor["linescores"]))
                _LOGGER.debug("%s: set_golf_values() 8: %s", sensor_name, competitor["linescores"][x]["value"])
                _LOGGER.debug("%s: set_golf_values() 8: %s", sensor_name, competition["competitors"][oppo_index]["linescores"][x]["value"])

                if (int(competitor["linescores"][x]["value"]) > int(competition["competitors"][oppo_index]["linescores"][x]["value"])):
                    new_values["team_score"] = new_values["team_score"] + 1
                else:
                    new_values["opponent_score"] = new_values["opponent_score"] + 1

        new_values["last_play"] = ''
        try:
            sets = len(competitor["linescores"])
        except:
            sets = 0

        _LOGGER.debug("%s: set_golf_values() 6: %s", sensor_name, sensor_name)

        for x in range (0, sets):
            new_values["last_play"] = new_values["last_play"] + " Set " + str(x + 1) + ": "
            new_values["last_play"] = new_values["last_play"] + competitor["athlete"]["shortName"] + " "
            try:
                new_values["last_play"] = new_values["last_play"] + str(int(competitor["linescores"] [x] ["value"])) + " "
            except:
                new_values["last_play"] = new_values["last_play"] + "?? "
            new_values["last_play"] = new_values["last_play"] + competition["competitors"][oppo_index]["athlete"]["shortName"] + " "
            try:
                new_values["last_play"] = new_values["last_play"] + str(int(competition["competitors"][oppo_index] ["linescores"] [x] ["value"])) + "; "
            except:
                new_values["last_play"] = new_values["last_play"] + "??; "

        new_values["team_sets_won"] = 0
        new_values["opponent_sets_won"] = 0
        for x in range (0, sets - 1):
            try:
                if competitor["linescores"][x]["value"] > competition["competitors"][oppo_index]["linescores"][x]["value"]:
                    new_values["team_sets_won"] = new_values["team_sets_won"] + 1
                else:
                    new_values["opponent_sets_won"] = new_values["opponent_sets_won"] + 1
            except:
                new_values["team_sets_won"] = new_values["team_sets_won"]


    if (new_values["sport"] == "mma"):
        try:
            new_values["team_score"] = competitor["linescores"][-1]["value"]
        except:
            new_values["team_score"] = None
        try:
            new_values["opponent_score"] = competition["competitors"][oppo_index]["linescores"][-1]["value"]
        except:
            new_values["opponent_score"] = None


    if (new_values["sport"] == "racing"):
        new_values["team_score"] = index + 1
        new_values["opponent_score"] = oppo_index + 1
        
    return new_values




async def get_golf_position(competition, index) -> str:

    t = 0
    tie = ""
    for x in range (1, index + 1):
        if competition["competitors"][x]["score"] == competition["competitors"][t]["score"]:
            tie = "T"
        else:
            tie = ""
            t = x
    try:
        if competition["competitors"][index]["score"] == competition["competitors"][index + 1]["score"]:
            tie = "T"
    except:
        tie = tie

    return tie + str(t + 1)


async def set_tennis_values(old_values, event, competition, competitor, lang, index) -> dict:
    new_values = {}

    if index == 0:
        oppo_index = 1
    else:
        oppo_index = 0

    new_values["key"] = "value"

    new_values["sport"] = old_values["sport"]
    new_values["league"] = old_values["league"]
    new_values["team_abbr"] = old_values["team_abbr"]
    new_values["opponent_abbr"] = None

    try:
        new_values["state"] = competition["status"]["type"]["state"].upper()
    except:
        new_values["state"] = event["status"]["type"]["state"].upper()

    try:
        new_values["date"] = competition["date"]
    except:
        new_values["date"] = event["date"]

    new_values["kickoff_in"] = arrow.get(new_values["date"]).humanize(locale=lang)

    try:
        new_values["venue"] = competition["venue"]["fullName"]
    except:
        new_values["venue"] = None

    try:
        new_values["location"] = "%s, %s" % (competition["venue"]["address"]["city"], competition["venue"]["address"]["state"])
    except:
        try:
            new_values["location"] = competition["venue"]["address"]["city"]
        except:
            new_values["location"] = None

    try:
        new_values["tv_network"] = competition["broadcasts"][0]["names"][0]
    except:
        new_values["tv_network"] = None

    try:
        new_values["odds"] = competition["odds"][0]["details"]
    except:
        new_values["odds"] = None

    try:
        new_values["overunder"] = competition["odds"][0]["overUnder"]
    except:
        new_values["overunder"] = None

    try:
        new_values["clock"] = competition["status"]["type"]["shortDetail"]
    except:
        try:
            new_values["clock"] = event["status"]["type"]["shortDetail"]
        except:
            new_values["clock"] = None

#    new_values["team_abbr"] = competitor["team"]["abbreviation"]
    new_values["team_id"] = competitor["id"]
    new_values["opponent_id"] = competition["competitors"][oppo_index]["id"]

    new_values["team_name"] = competitor["athlete"]["displayName"]
    new_values["opponent_name"] = competition["competitors"][oppo_index]["athlete"]["displayName"]

    try:
        new_values["team_record"] = competitor["records"][0]["summary"]
    except:
        new_values["team_record"] = None
    try:
        new_values["opponent_record"] = competition["competitors"][oppo_index]["records"][0]["summary"]
    except:
        new_values["opponent_record"] = None


    try:
        new_values["team_rank"] = competitor["tournamentSeed"]
    except:
        new_values["team_rank"] = None
    try:
        new_values["opponent_rank"] = competition["competitors"][oppo_index]["tournamentSeed"]
    except:
        new_values["opponent_rank"] = None


    try:
        new_values["team_logo"] = competitor["athlete"]["flag"]["href"]
    except:
        new_values["team_logo"] = DEFAULT_LOGO
    try:
        new_values["opponent_logo"] = competition["competitors"][oppo_index]["athlete"]["flag"]["href"]
    except:
        new_values["opponent_logo"] = DEFAULT_LOGO



    try:
        new_values["team_score"] = competitor["score"]
    except:
        new_values["team_score"] = None
    try:
        new_values["opponent_score"] = competition["competitors"][oppo_index]["score"]
    except:
        new_values["opponent_score"] = None

    return new_values