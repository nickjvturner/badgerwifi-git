' Selected image(s) are resized to 10 cm in height
Sub resize_selected_images_to_10cm_height()
    Dim shape As InlineShape
'     iterate all selected shapes
    For Each shape In Selection.InlineShapes
'         preserve aspect ratio
        shape.LockAspectRatio = msoTrue
'         set height to 10 cm
        shape.Height = CentimetersToPoints(10)
'         Optionally centre align image
'         shape.Range.ParagraphFormat.Alignment = wdAlignParagraphCenter
    Next
End Sub


' Selected image(s) are rotated designated number of degrees
Sub rotate_all_images_in_selection()
  Dim objInlineShape As InlineShape
  Dim objShape As shape
  Dim strDegree As String

  Application.ScreenUpdating = False

  strDegree = InputBox("Enter a rotation degree: ")
  Set objDoc = ActiveDocument

  For Each objInlineShape In Selection.InlineShapes
    Set objShape = objInlineShape.ConvertToShape
    objShape.IncrementRotation strDegree
    Set objInlineShape = objShape.ConvertToInlineShape
  Next objInlineShape

  Application.ScreenUpdating = True
End Sub


'Resize All images in document to x if taller than y
Sub resize_all_images_down_to_16H_if_taller()
Dim pic As Long
With ActiveDocument
For pic = 1 To .InlineShapes.Count
    With .InlineShapes(pic)
 If .Height > CentimetersToPoints(16) Then
    .Height = CentimetersToPoints(10)
End If
End With
Next pic
End With
End Sub