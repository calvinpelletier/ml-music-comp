var socket = io.connect('http://' + document.domain + ':' + location.port);

function add(_title, _song_url) {
    socket.emit('add', {
        party_url: window.location.href,
        title: _title,
        song_url: _song_url,
    });
}

socket.on('new_song', function (message){
	if (message)
	{
		$('.current_song_title').text(message["title"]);
	}
	else
	{
		$('.current_song_title').text("No song is playing");
	}
});

$(document).ready(function() {
	// audiojs.events.ready(function() {
    // 	var as = audiojs.createAll();
	// });
	// // $('#song').attr('autoplay','autoplay');
	// $('#song').play();
});
