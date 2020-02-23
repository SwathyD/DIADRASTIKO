const recordAudio = () => {
    return new Promise(resolve => {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                const mediaRecorder = new MediaRecorder(stream);
                const audioChunks = [];

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                const play = () => {
                    mediaRecorder.start();
                };

                const pause = () => {
                    mediaRecorder.stop();
                };

                const stop = () => {
                    return new Promise(resolve => {
                        mediaRecorder.addEventListener("stop", () => {
                            const audioBlob = new Blob(audioChunks);

                            audioBlob.arrayBuffer().then(function(rayBuffer){
                                resolve({rayBuffer})
                            })

                        });

                        mediaRecorder.stop();
                    });
                };

                resolve({ play, stop, pause });
            });
    });
};