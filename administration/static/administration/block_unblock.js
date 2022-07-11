
$(document).on('click', '.block_status', function() {
    var user_id = $(this).attr('data-user_id')
    var data_status = $(this).attr('data-status')
    if (data_status==='1'){
        let message = prompt("Please Enter why you want to block the user");
        if(message === "" || message === null){
            alert('Please enter something');
        }
        else{
            data = {'user_id':user_id,'data_status':data_status,'message':message}
            $.ajax({
                type:"POST",
                data : JSON.stringify(data),
                url:"/administration/block_unblock/",
                success:function(response){
                    alert("Blocked Successfully")
                    $('.block_status_'+user_id).remove()
                    var select_html = ""
                    select_html += "<div class=unblock_status_"+user_id+"><span style=margin-right:30px;>Would you like to Unblock ?</span><button type='button' data-user_id="+user_id+" data-status='0' class='btn btn-outline-info block_status'>Unblock</button></div>"
                    $('.action_button_'+user_id).append(select_html)
                }
            })
        }
    }
    else{
        data = {'user_id':user_id,'data_status':data_status}
        $.ajax({
            type:"POST",
            data : JSON.stringify(data),
            url:"/administration/block_unblock/",
            success:function(response){
                alert("Unblocked Successfully")
                   $('.unblock_status_'+user_id).remove()
                   var select_html = ""
                   select_html += "<div class=block_status_"+user_id+"><span style=margin-right:30px;>Would you like to Block ?</span><button type='button' data-user_id="+user_id+" data-status='1' class='btn btn-outline-danger block_status'>Block</button></div>"
                   $('.action_button_'+user_id).append(select_html)
            }
        })
    }
})
