$(document).ready(function(){
    $('#id_type_interview').change(function(){
        var type_interview_id = $(this).val()
        var csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
        data = {'type_interview_id':type_interview_id}
        if( type_interview_id != ""){
            $.ajax({
               type : 'POST',
               url : '/get_interviewers/',
               data: JSON.stringify(data),
                success:function(response){
                    console.log(response)
                    if(response["success"] == true){
                       var interviewers = response.interviewers
                       console.log(interviewers)
                       if (interviewers != ""){
                            var select_html = ''
                            $("#id_interviewer").empty()
                            select_html += "<option value=''>-- Select --</option>"
                            $(interviewers).each(function( i ){
                                select_html += "<option value="+interviewers[i]['id']+">"+interviewers[i]['username']+"</option>"
                            });
                            $("#id_interviewer").append(select_html)
                       }
                    }
                }
            })
        }
    })
    $("#get_slots").click(function(){
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
                     console.log(timings)
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
                 }
            })
        }
    })
})