$(document).on('change','#id_type_interview', function(){
    var type_interview_id = $(this).val()
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    data = {'type_interview_id':type_interview_id}
    if( type_interview_id != ""){
        $.ajax({
           type : 'POST',
           url : '/get_interviewers/',
           data: JSON.stringify(data),
            success:function(response){
                if(response["success"] == true){
                   var interviewers = response.interviewers
                    var select_html = ''
                    select_html += "<option value=''>-- Select --</option>"
                    $(interviewers).each(function( i ){
                        select_html += "<option value="+interviewers[i]['id']+">"+interviewers[i]['username']+"</option>"
                    });
                    $("#id_interviewer").html(select_html)
                }
            }
        })
    }
})

$(document).on('click','#get_slots',function(){
    var interviewer_id = $("#id_interviewer").val()
    var sch_date = $("#id_interview_date").val()
    var applicant_id = $("#applicant_id").val()
    data = {'sch_date':sch_date, 'interviewer_id':interviewer_id, 'applicant_id':applicant_id}
    if(interviewer_id != "" && sch_date != ""){
        $.ajax({
            type : "POST",
            url : '/get_time_slot/',
            data : JSON.stringify(data),
             success:function(response){
                 var timings = response.final_time_slot
                 $("#div_id_interview_time").show()
                 $("#interview_submit_btn").show()
                 $('#get_slots').hide()
                 if (timings != ""){
                    var select_html = ''
                    $(timings).each(function(i){
                        select_html += "<option value="+timings[i]+">"+timings[i]+"</option>"
                    });
                    $('#id_interview_time').html(select_html)
                 }
                 else{
                     var select_html = '<option>------<option>'
                     $('#id_interview_time').html(select_html)
                 }
             }
        })
    }
})
