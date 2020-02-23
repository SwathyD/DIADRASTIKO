var total_duration = 0
var fake_duration = 0
var pause_time = 0

var duration_display_interval_id = null
var is_recording = false

var before_pause_delay = 0
var after_play_delay = 0
var recent_most_command_ka_absolute_time = 0

var commands = []

e.on('change', function(evt){

    if(is_recording){   //useless check coz changes can be done only while recording
        var current_ts = new Date().getTime()

        var ts = current_ts - recent_most_command_ka_absolute_time + before_pause_delay;
        
        switch(evt.action){
            case "insert":
                
                commands.push({
                    type: "insert",
                    data:{
                        at:{
                            row: evt.start.row,
                            col: evt.start.column
                        },
                        char: evt.lines[0]
                    },
                    timestamp: ts
                })
                
                break
                
                case "remove":
                    
                    commands.push({
                        type: "delete",
                        data: {
                            at: {
                                row: evt.start.row,
                                col: evt.start.column
                            }
                        },
                        timestamp: ts
                    })
                    
                    break
                }
        
        before_pause_delay = 0
        recent_most_command_ka_absolute_time = current_ts
    }

}, false)
        
function playRecording() {

    if(!is_recording){
        start_offset = new Date().getTime()
        recent_most_command_ka_absolute_time = start_offset

        audioRecorder.play()
    
        duration_display_interval_id = setInterval(function(){
            fake_duration++
            timeElapsedSpan.innerText = fake_duration + "s"
        }, 1000)

        play_btn.style.color = "rgba(0, 0, 0, 0.2)"
        pause_btn.style.color = "rgba(0, 0, 0, 1)"
        stop_btn.style.color = "rgba(255, 0, 0, 1)"

        is_recording = true
        e.setReadOnly(false)
    }

}

function stopRecording() {

    if(is_recording){
        total_duration += new Date().getTime() - start_offset
    }

    if(total_duration > 0){

        play_btn.style.color = "rgba(0, 0, 0, 0.2)"
        pause_btn.style.color = "rgba(0, 0, 0, 0.2)"
        stop_btn.style.color = "rgba(255, 0, 0, 0.2)"
        play_btn.style.opacity = "0.2"

        if(!is_recording){
            audioRecorder.play()
        }

        audioRecorder.stop().then(function(audioBlob){
            loading_container.innerHTML = "<button onclick = 'sendDataToServer()' class='btn btn-success'>Publish</button>"
            
            window.audioBlob = new Uint8Array( audioBlob.rayBuffer )
        })

        clearInterval(duration_display_interval_id)
        
        timeElapsedSpan.innerText = (total_duration/1000).toFixed(2) + "s"

        is_recording = false
        e.setReadOnly(true)

        showPublishingModal()
    }
}

function pauseRecording() {

    if(is_recording){
        pause_time = new Date().getTime()

        before_pause_delay += pause_time - recent_most_command_ka_absolute_time 

        total_duration += pause_time - start_offset
        fake_duration = parseInt(total_duration/1000)
        timeElapsedSpan.innerText = fake_duration + "s"


        audioRecorder.pause()
        clearInterval(duration_display_interval_id)
    
        play_btn.style.color = "rgba(0, 0, 0, 1)"
        pause_btn.style.color = "rgba(0, 0, 0, 0.2)"
        
        is_recording = false
        e.setReadOnly(true)
    }
}

var editor = document.getElementById("editor")

var start_offset = 0
var pause_time = 0
var next_command = 0
var prev_timestamp = 0
var command_timeout_id = null
var should_dump_original = false //used only when editing is done

recordAudio().then(function(ar){
    window.audioRecorder = ar
})

function executeCode() {

    editor_output.innerText = ""
    editor_output.style.color = "black"

    if(is_recording){
        var current_ts = new Date().getTime()
        var ts = current_ts - recent_most_command_ka_absolute_time + before_pause_delay;

        commands.push({
            type: "execute",
            timestamp: ts
        })

        before_pause_delay = 0
        recent_most_command_ka_absolute_time = current_ts
    }

    if (!file_name.endsWith("html")) {
        fetch("/executeCode", {
            method: "POST",
            body: JSON.stringify({ file_name: file_name, src_code: e.getValue() })
        }).then(function (response) {
            response.text().then(function (txt) {

                var resp = JSON.parse(txt)

                if (resp['err'] != null) {
                    editor_output.style.color = "red"
                    editor_output.innerText = resp['err']
                } else {
                    editor_output.innerText = resp['out']
                }

            })
        })
    } else {
        editor_output.innerHTML = e.getValue()
    }

}

function showPublishingModal() {

    modal_showing_btn.click()

}

function sendDataToServer() {

    fetch('/uploadVideo/'+video_id, {
        method: "POST",
        body: JSON.stringify(
            { 
                commands: commands,
                audioBlob: audioBlob,
                total_duration: total_duration
            }
        )
    }).then(function(){
        window.location.href = "/";
    })

}