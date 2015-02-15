class_members = [$classMembers]

$("#id").val($id)
$("#name").val("$name");
$("#description").val("$description");

for (it=0;it<class_members.length;it++) {
    selectPupil(class_members[it]);
}

if ($selectedOnly == 1) {
    $("#show_selected").attr("checked","true");
}
selectedOnly = $selectedOnly;
populateTable();