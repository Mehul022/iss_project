function dragOverHandler(event) {
    event.preventDefault();
    document.getElementById('drop-area').style.border = '2px dashed #2ecc71';
}

function dropHandler(event) {
    event.preventDefault();
    document.getElementById('drop-area').style.border = '2px dashed #3498db';

    const files = event.dataTransfer.files;
    handleFiles(files);
}

function handleFiles(files) {
const preview = document.getElementById('image-preview');
const deleteAllBtn = document.getElementById('delete-all-btn');
deleteAllBtn.style.display = 'block';

const checkboxesContainer = document.getElementById('image-checkboxes');
checkboxesContainer.innerHTML = '';

for (const file of files) {
    // Check if the file is an image (jpeg, jpg, png, gif)
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'image-container';
            imgContainer.style.opacity = '0';

            const img = document.createElement('img');
            img.src = e.target.result;
            img.onload = function () {
                imgContainer.style.opacity = '1';
                imgContainer.classList.add('loaded');
            };

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerText = 'Delete';
            deleteBtn.addEventListener('click', function () {
                imgContainer.remove();
                updateImageCheckboxes();
                checkPreviewEmpty();
            });

            const checkboxContainer = document.createElement('div');
            checkboxContainer.className = 'checkbox-below-image';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = '';
            checkboxContainer.appendChild(checkbox);

            const durationInput = document.createElement('input');
            durationInput.type = 'number';
            durationInput.value = document.getElementById('image-duration').value;
            durationInput.min = '1'; // Minimum duration
            durationInput.step = '1'; // Duration step
            durationInput.disabled = true;

            // Save the duration value in the data attribute of the image container
            imgContainer.dataset.duration = durationInput.value;

            durationInput.addEventListener('input', function () {
                // Update the duration value in the data attribute as the user types
                imgContainer.dataset.duration = this.value;
            });

            checkbox.addEventListener('change', function () {
                // Enable/disable the duration input based on checkbox state
                durationInput.disabled = !this.checked;
            });

            imgContainer.appendChild(img);
            imgContainer.appendChild(deleteBtn);
            imgContainer.appendChild(checkboxContainer);
            imgContainer.appendChild(document.createTextNode(' Duration: '));
            imgContainer.appendChild(durationInput);
            preview.appendChild(imgContainer);
            updateImageCheckboxes();
        };

        reader.readAsDataURL(file);
    } else {
        // Display a message or handle non-image files differently
        console.log('Invalid file type. Only image files are allowed.');
    }
}
}


function updateImageCheckboxes() {
    const checkboxesContainer = document.getElementById('image-checkboxes');
    checkboxesContainer.innerHTML = '';

    const images = document.querySelectorAll('#image-preview img');
    images.forEach((img, index) => {
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-below-image';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = index + 1; // Start indexing from 1
        checkbox.checked = false; // Set to false to make them unselected by default

        const durationInput = document.createElement('input');
        durationInput.type = 'number';
        durationInput.value = document.getElementById('image-duration').value;
        durationInput.min = '1'; // Minimum duration
        durationInput.step = '1'; // Duration step

        checkbox.addEventListener('change', function () {
            durationInput.disabled = !this.checked;
        });

        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(document.createTextNode(` Image ${index + 1} Duration:`));
        checkboxContainer.appendChild(durationInput);

        checkboxesContainer.appendChild(checkboxContainer);
    });
}

function handleBackgroundMusic(files) {
    const backgroundMusicInput = document.getElementById('background-video-input');
    const backgroundMusicFile = backgroundMusicInput.files[0];

    // Handle the background music file as needed, e.g., save it for later use
    console.log('Selected background music file:', backgroundMusicFile);

    // Play the selected background music
    document.getElementById('audio-player').src = URL.createObjectURL(backgroundMusicFile);
}

function deleteAll() {
    const preview = document.getElementById('image-preview');
    preview.innerHTML = '';
    const checkboxesContainer = document.getElementById('image-checkboxes');
    checkboxesContainer.innerHTML = '';
    checkPreviewEmpty();

    // Pause and reset the audio player
    const audioPlayer = document.getElementById('audio-player');
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
}

function checkPreviewEmpty() {
    const preview = document.getElementById('image-preview');
    const deleteAllBtn = document.getElementById('delete-all-btn');
    deleteAllBtn.style.display = preview.children.length > 0 ? 'block' : 'none';
}

document.getElementById('drop-area').addEventListener('click', function () {
    document.getElementById('fileInput').click();
});

function convertToVideo() {
    // You'll need to send the selected resolution and quality to the server for processing.
    const resolution = document.getElementById('resolution-selector').value;
    const quality = document.getElementById('quality-selector').value;

    // Make an AJAX request to the server to initiate video conversion with the specified parameters.
    // Example using fetch API:
    fetch('/convert-video', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            resolution,
            quality,
            // ... (other parameters, e.g., selected images, duration, etc.)
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response from the server, e.g., display a download link to the user.
        console.log('Video conversion result:', data);
    })
    .catch(error => {
        console.error('Error during video conversion:', error);
    });
}