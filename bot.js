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

var search_res = null;
var timer = null;
var searched = -1;
var sent = null;
client.on("message", (message) => {
    if( message.author.bot ) return; // if we sent skip...
    const args = message.content.split(/\s+/g);
    if( args.length == 1 && searched != 1 ){
        return;
    }
    const prefix = settings.bot.prefix;
    // youtube commands
    if( args[0].indexOf( prefix+"yt" ) > -1 ){
        if( searched == 1 ){
            return;
        }
        search_str = "";
        for( var i = 1; i < args.length; i++ ){
            search_str +=  args[i] + " ";
        }
        res_str = "";
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
        which = (args[0])-1; // users will index from 1 not 0
        uri = "https://www.youtube.com/watch?v="+search_res.items[which].id.videoId;
        message.channel.send( uri );
        if( timer != null ){
            clearTimeout(timer);
        }
        search_res = null;
    }
    else {
        console.log( "unknwown command" );
    }
});
