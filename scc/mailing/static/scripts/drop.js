$(function() {
    $('#dropContainer').on('dragover', function(e) {
        e.preventDefault();
    });
    $('#dropContainer').on('drop', function(e) {
        e.preventDefault();
        $('#fileInput').prop('files', e.originalEvent.dataTransfer.files);
        $('#fileInput').trigger('change');
    });

    $('#fileInput').on('change', function(e) {
        if ($(this)[0].files.length > 0) {
            let fileSize = $(this)[0].files[0].size / 1024 ** 2;
            if (fileSize > 2) {
                $('#file-result')[0].innerHTML = "Select file less than 2MB.";
                $('#file-import')[0].disabled = true;
            } else {
                $('#file-import').disabled = false;
            }
        }
    });
    
    $('#msg-attachments').on('dragover', function(e) {
        e.preventDefault();
    });
    $('#msg-attachments').on('drop', function(e) {
        e.preventDefault();
        $('#msg-attachments').prop('files', '');
        $('#msg-attachments').prop('files', e.originalEvent.dataTransfer.files);
        $('#msg-attachments').trigger('change');
    });

    $('#msg-attachments').on('change', function(e) {
        if ($(this)[0].files.length > 0) {
            console.log($(this)[0].files.length);
            let filesSize = 0;
            $.each($(this)[0].files, function(i, val) {
                console.log(val.size);
            });
            
            //size / 1024 ** 2;

            if (filesSize > 20) {
                $('#attachments-result')[0].innerHTML = "Select file less than 20MB.";
                $('#send-mails')[0].disabled = true;
            } else {
                $('#send-mails').disabled = false;
            }
        }
    });
});