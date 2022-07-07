 $(document).ready(function(){
    $(".remove_job").click(function(){
        var job_id = $(this).attr("data-job_id")
        var csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
        data = {"job_id" : job_id}
        $.ajax({
            type: "DELETE",
            data: JSON.stringify(data),
            url : "/career/",
            headers : {
                'X-CSRFToken' : csrf_token
            },
            success:function(response){
                if(response["success"] == true){
                    var test = $(".my_jobs_openings .jobs_openings").length
                    if (test == 1) {
                        $("<p class='alert alert-danger'>No Jobs Found</p>").insertAfter(".my_jobs_openings .job_header");
                    }
                    alert(response["message"])
                    $("#"+job_id).remove()
                }
            }
        })
    })
})