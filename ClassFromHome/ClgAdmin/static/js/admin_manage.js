$(document).ready(function(){

var admin_ac_id;


$("#id_stud_file_id").on("change", function() {
  alert("file_input");
  console.log("HIIIIIIII");
  var fileName = $(this).val().split("\\").pop();
  $("#stud_file_id").addClass("selected").html(fileName);
});
}





