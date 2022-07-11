$(document).on('click','.accept_reject_status',function(){
    var data_value = $(this).attr('data-value')
    var application_id = $(this).attr('data-user_id')
    data = {'data_value':data_value,'application_id':application_id}
    console.log(data)
    if(data != ""){
        $.ajax({
            type : 'POST',
            data : JSON.stringify(data),
            url : '/collect_final_status/',
             success:function(response){
                var msg = response.message
                alert(msg);
                $('.acceptance_status_'+application_id).remove()
             }
        })
    }
})