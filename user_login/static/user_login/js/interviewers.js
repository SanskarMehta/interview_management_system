$(document).ready(function(){
    $(".remove_interviewer").click(function(){
        var interviewer_id = $(this).attr("data-interviewer_id")
        data = {"interviewer_id" : interviewer_id}
        $.ajax({
            type: "DELETE",
            data: JSON.stringify(data),
            url : "/show_interviewers/",
            success:function(response){
                if(response["success"] == true){
                    alert(response["message"])
                    $("#"+interviewer_id).remove()
                }
            }
        })
    })
})