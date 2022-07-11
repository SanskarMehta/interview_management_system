$(document).on('change','#date', function(){
    var send_data = $(this).val()
    var date = new Date(Date.parse($(this).val(),'yyyy/MM/dd'))
    var today = new Date();
    var current_date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var current_date1 = new Date(Date.parse(current_date,'yyyy/MM/dd'))
    var interviewer_id = $("#interviewer_id").attr('data-interviewer_id')
    var applicant_id = $("#applicant_id").attr('data-application_id')
    data = {'sch_date':send_data, 'interviewer_id':interviewer_id, 'applicant_id':applicant_id}
    if (date > current_date1){
        $('input[type="submit"]').show()
        $.ajax({
            type : "POST",
            url : '/get_reschedule_time_slot/',
            data : JSON.stringify(data),
             success:function(response){
                 var timings = response.final_time_slot
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
    else{
        alert('Invalid Date')
        $('input[type="submit"]').hide()
    }
})
