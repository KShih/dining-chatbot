// Version2: User(After Cognito) -> Lex
// https://aws.amazon.com/tw/blogs/machine-learning/greetings-visitor-engage-your-web-users-with-amazon-lex/

// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:05f41a9e-609b-43dd-bd77-a0fbeedcda16',
});


var lexruntime = new AWS.LexRuntime();
var lexUserId = 'BookResturant' + Date.now();
var sessionAttributes = {};


var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function() {
    $messages.mCustomScrollbar();
    setTimeout(function() {
        // bot greeting msg
    }, 100);
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    console.log("hiiii");
    let msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }

    sendApi(msg);
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();

}


function sendApi(msg) {
    var params = {
        botAlias: '$LATEST',
		botName: 'BookResturant',
		inputText: msg,
		userId: lexUserId,
		sessionAttributes: sessionAttributes
    };

    lexruntime.postText(params, function(err, data) {
		if (err) {
			console.log(err, err.stack);
			data = 'Error:  ' + err.message + ' (see console for details)'
		}
		if (data) {
			// capture the sessionAttributes for the next cycle
			sessionAttributes = data.sessionAttributes;
			// show response and/or error/dialog status
            botReplyMessage(data);
		}
	});

}


$('.message-submit').click(function() {
    insertMessage();
});

$(window).on('keydown', function(e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})

function botReplyMessage(result) {
    console.log("botReplyMessage", result);
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
        $('.message.loading').remove();
        // Put bot answering msg here
        // TODO:

        $('<div class="message new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure>' + result.message + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
        i++;
    }, 1000 + (Math.random() * 20) * 100);

}
