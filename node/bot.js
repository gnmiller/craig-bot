const Discord = require( "discord.js" );
const client = new Discord.Client();
const settings = require( "./settings.json" );
const YouTube = require( "youtube-node" );
var yt = new YouTube();

// login to discord
client.login( settings.discord.token );

// login to youtube
yt.setKey( settings.youtube.token );

client.on("ready", () => {
});

search_res = null;
timer = null;
searched = -1;
sent = null;
client.on("message", (message) => {
    if( message.author.bot ){
        console.log( "bot is the author" );
        return;
    }
    const args = message.content.split(/\s+/g);
    const prefix = settings.bot.prefix;
    if( args[0][0].indexOf( prefix ) < 0 ){
        console.log( "prefix not detected" );
        return;
    }
    // youtube commands
    if( args[0].indexOf( prefix+"yt" ) > -1 ){
        if( searched == 1 ){
            return;
        }
        var search_str = "";
        for( var i = 1; i < args.length; i++ ){
            search_str +=  args[i] + " ";
        }
        var res_str = "";
        yt.search( search_str, 10, function( error, result ) {
            // store results globally for later parsing
            search_res = result;
            if( error ){
                console.log( error );
            } else {
                // build results
                res_str += "\n\n```css\n";
                for( var i = 0; i < result.items.length; i++ ){
                    title = result.items[i].snippet.title;
                    id = result.items[i].id.videoId;
                    desc = result.items[i].snippet.description;
                    t_str = (i+1)+". "+title+" -- "+desc;
                    if( t_str.length > 80 ) res_str += t_str.substring(0,80)+"...\n";
                    else res_str += t_str+"\n";
                }
                res_str += "```";
                searched = 1;
                timer = setTimeout( function () {
                    searched = 0;
                    timer = null;
                    message.channel.send( "Timeout!" );
                }, 10000, 'yt_timeout' );
                sent = message.channel.send( res_str );
            }
        });
    } else if( searched == 1 ){ // get specific youtube video from results
        searched = 0;
        var which = (args[0])-1; // users will index from 1 not 0
        var uri = "https://www.youtube.com/watch?v="+search_res.items[which].id.videoId;
        message.channel.send( uri );
        if( timer != null ){
            clearTimeout(timer);
        }
        search_res = null;
    } else if( args[0].indexOf( prefix+"got" ) > -1 ){
        var time_left = got_time();
    }
    else {
        console.log( "unknwown command" );
    }
});

function got_time( ){
    var req = require( "request" );
    var moment = require( "moment" );
    var got_uri = "http://api.tvmaze.com/shows/82?embed=nextepisode";
    var ret = "";
    var t = null;
    req({
        url: got_uri,
        json: true
    }, function( error, resp, body, callback ){
        if( !error && resp.statusCode == 200 ){
            t = body;
            callback( t );
        }
    });
    console.log( t );
}
