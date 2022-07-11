$(document).on('click','.cv_status', function(){
    var acceptance_status = $(this).attr('data-status')
    var company_id = $(this).attr('data-company_id')
    data = {'acceptance_status':acceptance_status , 'company_id':company_id}
    $.ajax({
        type : 'POST',
        url : '/administration/company_accept_reject/',
        data : JSON.stringify(data),
         success:function(response){
            if( acceptance_status ==='0'){
                $('.accept_status_'+company_id).remove()
                alert('Company is accepted')
            }
            else{
                $('.reject_status_'+company_id).remove()
                alert('Company is Rejected')
            }
         }
    })
})