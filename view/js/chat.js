// Version1: User(Through API Gateway SDK) -> (API Gateway-> Lambda) -> Lex

var apigClient = apigClientFactory.newClient();

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
    let msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }
    // send the user input msg here
    sendApi(msg).then( function(result){
        $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        $('.message-input').val(null);
        updateScrollbar();
        botReplyMessage(result);
    });
}


function sendApi(msg) {
    var params = {
    };
    var body = {
        // This is where you define the body of the request,

        "messages": [{
            "type": "string",
            "unstructured": {
                "id": 0,
                "text": msg,
                "timestamp": "string"
            }
        }]
    };
    var additionalParams = {
    };

    return apigClient.chatbotPost(params, body, additionalParams)
        .then(function(result) {
            // Add success callback code here.
            return result;
        }).catch(function(result) {
            return result;
            // Add error callback code here.
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
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
        $('.message.loading').remove();
        // Put bot answering msg here
        // TODO:

        $('<div class="message new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure>' + result.data.message + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
        i++;
    }, 1000 + (Math.random() * 20) * 100);

}
