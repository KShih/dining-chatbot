var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function() {
    $messages.mCustomScrollbar();
    setTimeout(function() {
        fakeMessage();
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
    // TODO:
    sendApi(msg);

    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    setTimeout(function() {
        fakeMessage();
    }, 1000 + (Math.random() * 20) * 100);
}

var botReply = ""

function sendApi(msg) { // should i put let here?
    var params = {
        // This is where any modeled request parameters should be added.
        // The key is the parameter name, as it is defined in the API in API Gateway.
        // param0: '',
        // param1: ''
    };

    var body = {
        // This is where you define the body of the request,

        "messages": [{
            "type": "string",
            "unstructured": {
                "id": 0,
                "text": "Hi, this is testing message",
                "timestamp": "string"
            }
        }]
    };

    var additionalParams = {
        // If there are any unmodeled query parameters or headers that must be
        //   sent with the request, add them here.
        // headers: {
        //   param0: '',
        //   param1: ''
        // },
        // queryParams: {
        //   param0: '',
        //   param1: ''
        // }
    };

    apigClient.methodName(params, body, additionalParams)
        .then(function(result) {
            // Add success callback code here.
            botReply = result;
        }).catch(function(result) {
            // Add error callback code here.
            botReply = {
                "messages": [{
                    "type": "string",
                    "unstructured": {
                        "id": 0,
                        "text": "Error occur, please try again",
                        "timestamp": "string"
                    }
                }]
            };
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

function fakeMessage() {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
        $('.message.loading').remove();
        // Put bot answering msg here
        // TODO:

        $('<div class="message new"><figure class="avatar"><img src="assets/media/food_robot.png" /></figure>' + botReply.messages.text + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
        i++;
    }, 1000 + (Math.random() * 20) * 100);

}
