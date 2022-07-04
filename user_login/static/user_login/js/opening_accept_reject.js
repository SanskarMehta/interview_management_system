$(document).on('click', '.cv_status', function(){
    var user_applied_job_id = $(this).attr('data-userjob_id')
    var data_status = $(this).attr('data-status')
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    console.log(user_applied_job_id)
    data = {'user_applied_job_id':user_applied_job_id, "data-status": data_status}
    $.ajax({
        type: "POST",
        data: data,
        url : "/show_applicants/",
        headers : {
            'X-CSRFToken' : csrf_token
        },
        success:function(response){
            if(response["success"] == true){
                if(data_status == 0)
                {
                    $("#status_"+user_applied_job_id).empty()
                    $(".accept_status_"+user_applied_job_id).remove()
                    $("#status_"+user_applied_job_id).html('<span class="alert alert-success" role="alert" style="margin-left:5px;">Status : <b>Accepted</b></span>')
                }
                else{
                    $(".reject_status_"+user_applied_job_id).remove()
                    $("#status_"+user_applied_job_id).empty()
                    $("#status_"+user_applied_job_id).html('<span class="alert alert-danger" role="alert" style="margin-left:5px;">Status : <b>Rejected</b></span>')
                }
            }
         }
    })
})