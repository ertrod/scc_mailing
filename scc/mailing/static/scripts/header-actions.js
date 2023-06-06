
// delete row from table
function DeleteRow(obj) {
    let parent = obj.parentNode.parentNode;
    parent.parentNode.removeChild(parent);
}

$(function () {
    // select all checkboxes
    $('#select-all').click(function (event) {
        if (this.checked) {
            // Iterate each checkbox
            $('input[name="checked-users"]').each(function () {
                this.checked = true;
            });
        } else {
            $('input[name="checked-users"]').each(function () {
                this.checked = false;
            });
        }
    });

    $('input[name="checked-users"]').change(function (event) {
        if (!this.checked) {
            $('#select-all').prop('checked', false);
        }

    });

    // mark required fields on user
    $(':input[required]').parent().prev('th').children().addClass('marked');

    $('[id^="select-all-"]').click(function (event) {
        let id = this.value;
        if (this.checked) {
            $('input[name="checked-groups-' + id + '"]').each(function (){
                this.checked = true;
            });
        } else {
            $('input[name="checked-groups-' + id + '"]').each(function (){
                this.checked = false;
            });
        }
    });


    $('#select-all-groups').click(function (event) {
        setTimeout(function () {
            $('input:checkbox[name=checked-groups]').trigger('change');
        }, 10);
        if (this.checked) {
            $('input[name="checked-groups"]').each(function () {
                this.checked = true;
            });
        } else {
            $('input[name="checked-groups"]').each(function () {
                this.checked = false;
            });
        }
    });

    $('#select-all-users').click(function (event) {
        if (this.checked) {
            // Iterate each checkbox
            $('input[name="checked-users"]').each(function () {
                this.checked = true;
            });
        } else {
            $('input[name="checked-users"]').each(function () {
                this.checked = false;
            });
        }
    });

    $('input:checkbox[name=checked-groups]').change(function (event) {
        let current_script = document.querySelector('script[data-url-groups]');
        let post_url = current_script.getAttribute('data-url-groups');
        let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        let groups = [];
        $('input:checkbox[name=checked-groups]:checked').each(function() {
            groups.push($(this).val());
        });
        $.ajax({
            url: post_url,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({groups: groups}),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            success: (data) => {
                    $('#users-table tbody').empty();
                    $.each(data.users, function(i, val) {
                        let tr = `<tr> \
                            <th scope="row">\
                                <input type="checkbox" value=${val.user.id} name="checked-users">\
                            </th>\
                            <td>${val.user.id}</td>\
                            <td>${val.user.login}</td>\
                            <td>`
                        $.each(val.emails, function(i, val) {
                            tr += `<pre>${val.email}</pre>`
                        });

                        tr += '</td>\
                            <td>'
                        $.each(val.groups, function(i, val) {
                            tr += `<pre>${val}</pre>`
                        });
                        
                        tr += `</td>\
                            <td>${ val.user.service_memo_number }</td>\
                            <td>${ val.user.service_registration_date }</td>\
                            <td>${ val.user.post }</td>\
                            <td>${ val.user.last_name }</td>\
                            <td>${ val.user.first_name }</td>\
                            <td>${ val.user.surname }</td>\
                            <td>${ val.user.number }</td>\
                            <td>${ val.user.school }</td>\
                            <td>${ val.user.department }</td>\
                            <td>${ val.user.science_project }</td>\
                            <td>${ val.user.science_mentor }</td>\
                            <td>${ val.user.commentary }</td>\
                        </tr>`
                        $('#users-table > tbody:last-child').append(tr);
                    });
                },
            error: (error) => {
                console.log(error);
            }
        });
    });

    // add row to email table
    $('[id^="add-row-email"]').each(function (index) {
        $(this).click(function (event) {
            let table = '#tbl-email' + $(this).val();
            let name = "new-email" + $(this).val();
            $(table).append('<tr>' +
                '<td><input type="email" name="' + name + '"></td>' +
                '<td><input type="button" class="btn btn-sm btn-outline-danger" value="Удалить" onclick="DeleteRow(this)"></td>' +
                '</tr>');
        });
    });

    $('#remove-users').click(function (event) {
        let ids = $('input[name="checked-users"]:checked').map(function () { return $(this).val(); }).get();
        if (ids.length > 0)
            return window.confirm('Удалить пользователей этих пользователей? ' + ids);
    });

    $('#template-delete').click(function (event) {
        return window.confirm('Удалить этот шаблон?');
    });

    $('#group-delete-confirm').click(function (event) {
        return window.confirm('Удалить эту группу?');
    });

    $('#send-mails').click(function (event) {
        let cbx = $("input:checkbox[id^='checked-']");
        cbx.prop('required', true);
        if (cbx.is(':checked')) {
            cbx.prop('required', false);
        }
    });

    // delete foreign key post
    $("[id^='foreign-post-']").each(function () {
        $(this).click(function (event) {
            let current_script = document.querySelector('script[data-url-post]');
            let post_url = current_script.getAttribute('data-url-post');
            let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            let closest_tr = $(this).closest('tr');
            let select = closest_tr.find('select')[0];
            let input = closest_tr.find('input')[0];
            let operation = $(this).context.getAttribute("data-operation");

            let value = input.value;
            let data_id = -1;
            let selected_value = $('#' + select.getAttribute('id') + " option:selected")[0];

            if (selected_value.value) 
                data_id = selected_value.getAttribute("data-id");
            else
                data_id = input.getAttribute('data-id');
            
            switch (operation) {
                case 'create':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({post: value, op: operation}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            if (!data.exists) {
                                $('[id^="foreign-post-create"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    let select = closest_tr.find('select')
                                    select.append('<option ' +
                                        `data_id="${data.id}"` +
                                        `name="user-posts"` +
                                        `value="${data.value}"` +
                                        `>${data.value}</option>`);
                                    });
                                };
                            },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'update':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({post: value, op: operation, id: data_id}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            $('[id^="foreign-post-update"]').each(function () { 
                                let closest_tr = $(this).closest('tr');
                                let select = closest_tr.find('select');
                                let option = select.find('option[data-id="' + data.id + '"]');
                                option.attr("value", data.value);
                                option.text(data.value);
                                closest_tr.find('[id^="input-post"]').each(function () {
                                    if ($(this).attr('data-id') == data_id)
                                        $(this).val(data.value);
                                });
                            });
                        },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'delete':
                    if (window.confirm("Удалить эту должность?")) {
                        $.ajax({
                            url: post_url,
                            type: 'POST',
                            dataType: 'json',
                            data: JSON.stringify({post: value, op: operation, id: data_id}),
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrftoken,
                            },
                            success: (data) => {
                                $('[id^="foreign-post-delete"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    closest_tr.find('select').find('[value="' + value + '"]').remove();
                                    closest_tr.find('[id^="input-post"]').each(function () {
                                        if ($(this).val() == value)
                                            $(this).val('');
                                    });
                                });
                            },
                            error: (error) => {
                                console.log(error);
                            }
                        });
                    }
                break;
            }

        });
    });

    // delete foreign key school
    $("[id^='foreign-school-']").each(function () {
        $(this).click(function (event) {
            let current_script = document.querySelector('script[data-url-school]');
            let post_url = current_script.getAttribute('data-url-school');
            let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            let closest_tr = $(this).closest('tr');
            let select = closest_tr.find('select')[0];
            let input = closest_tr.find('input')[0];
            let operation = $(this).context.getAttribute("data-operation");

            let value = input.value;
            let data_id = -1;
            let selected_value = $('#' + select.getAttribute('id') + " option:selected")[0];
            console.log(selected_value.value);

            if (selected_value.value) 
                data_id = selected_value.getAttribute("data-id");
            else
                data_id = input.getAttribute('data-id');

            console.log(data_id)
            
            switch (operation) {
                case 'create':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({school: value, op: operation}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            if (!data.exists) {
                                $('[id^="foreign-school-create"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    let select = closest_tr.find('select')
                                    select.append('<option ' +
                                        `data_id="${data.id}"` +
                                        `name="user-school"` +
                                        `value="${data.value}"` +
                                        `>${data.value}</option>`);
                                    });
                                };
                            },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'update':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({school: value, op: operation, id: data_id}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            $('[id^="foreign-school-update"]').each(function () { 
                                let closest_tr = $(this).closest('tr');
                                let select = closest_tr.find('select');
                                let option = select.find('option[data-id="' + data.id + '"]');
                                option.attr("value", data.value);
                                option.text(data.value);
                                closest_tr.find('[id^="input-school"]').each(function () {
                                    if ($(this).attr('data-id') == data_id)
                                        $(this).val(data.value);
                                });
                            });
                        },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'delete':
                    if (window.confirm("Удалить этот институт?")) {
                        $.ajax({
                            url: post_url,
                            type: 'POST',
                            dataType: 'json',
                            data: JSON.stringify({school: value, op: operation, id: data_id}),
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrftoken,
                            },
                            success: (data) => {
                                $('[id^="foreign-school-delete"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    closest_tr.find('select').find('[value="' + value + '"]').remove();
                                    closest_tr.find('[id^="input-school"]').each(function () {
                                        if ($(this).val() == value)
                                            $(this).val('');
                                    });
                                });
                            },
                            error: (error) => {
                                console.log(error);
                            }
                        });
                    }
                break;
            }

        });
    });
    
    // delete foreign key department
    $("[id^='foreign-department-']").each(function () {
        $(this).click(function (event) {
            let current_script = document.querySelector('script[data-url-department]');
            let post_url = current_script.getAttribute('data-url-department');
            let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            let closest_tr = $(this).closest('tr');
            let select = closest_tr.find('select')[0];
            let input = closest_tr.find('input')[0];
            let operation = $(this).context.getAttribute("data-operation");

            let value = input.value;
            let data_id = -1;
            let selected_value = $('#' + select.getAttribute('id') + " option:selected")[0];
            console.log(selected_value.value);

            if (selected_value.value) 
                data_id = selected_value.getAttribute("data-id");
            else
                data_id = input.getAttribute('data-id');

            console.log(data_id)
            
            switch (operation) {
                case 'create':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({department: value, op: operation}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            if (!data.exists) {
                                $('[id^="foreign-department-create"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    let select = closest_tr.find('select')
                                    select.append('<option ' +
                                        `data_id="${data.id}"` +
                                        `name="user-department"` +
                                        `value="${data.value}"` +
                                        `>${data.value}</option>`);
                                    });
                                };
                            },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'update':
                    $.ajax({
                        url: post_url,
                        type: 'POST',
                        dataType: 'json',
                        data: JSON.stringify({department: value, op: operation, id: data_id}),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrftoken,
                        },
                        success: (data) => {
                            $('[id^="foreign-department-update"]').each(function () { 
                                let closest_tr = $(this).closest('tr');
                                let select = closest_tr.find('select');
                                let option = select.find('option[data-id="' + data.id + '"]');
                                option.attr("value", data.value);
                                option.text(data.value);
                                closest_tr.find('[id^="input-department"]').each(function () {
                                    if ($(this).attr('data-id') == data_id)
                                        $(this).val(data.value);
                                });
                            });
                        },
                        error: (error) => {
                            console.log(error);
                        }
                    });
                break;
                case 'delete':
                    if (window.confirm("Удалить эту кафедру?")) {
                        $.ajax({
                            url: post_url,
                            type: 'POST',
                            dataType: 'json',
                            data: JSON.stringify({department: value, op: operation, id: data_id}),
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrftoken,
                            },
                            success: (data) => {
                                $('[id^="foreign-department-delete"]').each(function () { 
                                    let closest_tr = $(this).closest('tr');
                                    closest_tr.find('select').find('[value="' + value + '"]').remove();
                                    closest_tr.find('[id^="input-department"]').each(function () {
                                        if ($(this).val() == value)
                                            $(this).val('');
                                    });
                                });
                            },
                            error: (error) => {
                                console.log(error);
                            }
                        });
                    }
                break;
            }

        });
    });

    
});