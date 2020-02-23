//type: insert, delete, select

//current_code_buffer either points to original or user buffer

// var commands = [
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 0
//             },
//             char: "p"
//         },
//         timestamp: 500
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 1
//             },
//             char: "r"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 2
//             },
//             char: "i"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 3
//             },
//             char: "n"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 4
//             },
//             char: "t"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 5
//             },
//             char: "("
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 6
//             },
//             char: "\""
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 7
//             },
//             char: "H"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 8
//             },
//             char: "i"
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 9
//             },
//             char: "\""
//         },
//         timestamp: 1000
//     },
//     {
//         type: "insert",
//         data: {
//             at: {
//                 row: 0,
//                 col: 10
//             },
//             char: ")"
//         },
//         timestamp: 1000
//     }
// ]

// var file_name = "test.py" 

// var a = new Audio("/static/audio/sound.mp3")

a.onloadedmetadata = () => {
    seek_bar.max = total_duration/1000
    endTimeSpan.innerText = (total_duration/1000).toFixed(2) + "s"
}

// update audio position
seek_bar.onchange = () => {
    a.currentTime = seek_bar.value

    seek(parseInt(a.currentTime * 1000))
}

// update range input when currentTime updates
a.ontimeupdate = () => {
    seek_bar.value = a.currentTime
    currentTimeSpan.innerText = a.currentTime.toFixed(2) + "s"
}


var editor = document.getElementById("editor")

var original_code_buffer = []
var current_code_buffer = original_code_buffer

var start_offset = 0
var pause_time = 0
var next_command = 0
var prev_timestamp = 0
var command_timeout_id = null
var should_dump_original = false //used only when editing is done


function playVideo(){

    if(next_command < commands.length){
        command_timeout_id = setTimeout( perCommandAction, commands[next_command].timestamp - pause_time )
    }

    a.play()
}

function pauseVideo(){

    pause_time = new Date().getTime() - prev_timestamp
    clearInterval( command_timeout_id )

    a.pause()
} 

function seek(ms){
    pause_btn_clicked()

    var total = 0

    var temp_buffer = []

    current_code_buffer = temp_buffer

    var command_counter = 0
    
    while(  command_counter < commands.length
            && total + commands[command_counter].timestamp <= ms){

        doAction(commands[command_counter])
        total += commands[command_counter].timestamp
        
        command_counter++
        
    }

    original_code_buffer = temp_buffer
    current_code_buffer = original_code_buffer

    next_command = command_counter

    updateView()

    pause_time = ms - total

    play_btn_clicked()
}

function doAction(command){
    
    switch (command.type) {
        case "insert":

            insertCharAt(
                command.data.char,
                command.data.at.row,
                command.data.at.col
            )

            break
        
        case "delete":

            deleteCharAt(
                command.data.at.row,
                command.data.at.col
            )

            break

        case "execute":

                executeCode()
                
            break
    }

}


function perCommandAction(){

    doAction(commands[next_command])

    updateView()

    next_command++

    if(next_command < commands.length){
        prev_timestamp = new Date().getTime()
        pause_time = 0
        
        command_timeout_id = setTimeout(perCommandAction, commands[next_command].timestamp)
    }
}

function insertCharAt(char, row, col){

    if(current_code_buffer[row] == undefined){
        current_code_buffer[row] = ""
    }

    current_code_buffer[row] = current_code_buffer[row].substring(0, col) 
                                + char 
                                + current_code_buffer[row].substring( 
                                                    col, 
                                        current_code_buffer[row].length
                                    )
}

function deleteCharAt(row, col){
    current_code_buffer[row] = current_code_buffer[row].substring( 0, col )
                                + current_code_buffer[row].substring(
                                    col + 1,
                                    current_code_buffer[row].length
                                )
}

function updateView(){
    var txt = current_code_buffer.join("\n")

    e.setValue(txt)

    e.clearSelection()
}




//dev support

function stringToInserts(str, row){
    for(var i = 0; i < str.length; i++){
        insertCharAt(str[i], row, i)
    }
}

pause_btn_clicked()

//dom handlers
function play_btn_clicked(){
    if(!play_btn.disabled){
        
        if(should_dump_original){
            current_code_buffer = original_code_buffer
            updateView()

            should_dump_original = false
            edit_btn.style.color = "black"
        }

        playVideo()

        play_btn.disabled = true
        play_btn.style.color = "rgba(0, 0, 0, 0.2)"
        
        pause_btn.disabled = false
        pause_btn.style.color = "rgba(0, 0, 0, 1)"
    }
}

function pause_btn_clicked() {
    if (!pause_btn.disabled) {
        pauseVideo()

        pause_btn.disabled = true
        pause_btn.style.color = "rgba(0, 0, 0, 0.2)"

        play_btn.disabled = false
        play_btn.style.color = "rgba(0, 0, 0, 1)"
    }
}

function executeCode(){

    editor_output.innerText = ""
    editor_output.style.color = "black"

    if(!file_name.endsWith("html")){
        fetch("/executeCode", {
            method: "POST",
            body: JSON.stringify( { file_name: file_name, src_code: e.getValue()} )
        }).then(function(response){
            response.text().then(function(txt){
                
                var resp = JSON.parse(txt)
    
                if(resp['err'] != null){
                    editor_output.style.color = "red"
                    editor_output.innerText = resp['err']
                }else{
                    editor_output.innerText = resp['out']
                }
    
            })
        })
    }else{
        editor_output.innerHTML = e.getValue()
    }

}

function edit_btn_clicked(){
    pause_btn_clicked()

    e.setReadOnly(false)

    should_dump_original = true

    edit_btn.style.color = "green"
}