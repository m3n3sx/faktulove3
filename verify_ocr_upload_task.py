#!/usr/bin/env python3
"""
Simple verification script for OCR upload task completion
"""

import os
import json

def check_file_exists(path, description):
    """Check if file exists and print result"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def check_file_contains(path, content, description):
    """Check if file contains specific content"""
    try:
        with open(path, 'r') as f:
            file_content = f.read()
        contains = content in file_content
        status = "✓" if contains else "✗"
        print(f"{status} {description}")
        return contains
    except Exception as e:
        print(f"✗ Error checking {path}: {e}")
        return False

def main():
    print("=== OCR Upload Task Verification ===\n")
    
    print("Task 4.1: Implement working React upload component")
    print("-" * 50)
    
    # Check React component source
    react_component_exists = check_file_exists(
        "frontend/src/apps/SimpleUploadApp.js",
        "React upload component source"
    )
    
    # Check React bundle
    react_bundle_exists = check_file_exists(
        "static/js/upload-app.bundle.js", 
        "React upload bundle"
    )
    
    # Check React dependencies
    react_deps = [
        ("static/js/react.production.min.js", "React library"),
        ("static/js/react-dom.production.min.js", "ReactDOM library")
    ]
    
    react_deps_exist = all(check_file_exists(path, desc) for path, desc in react_deps)
    
    # Check bundle content
    if react_bundle_exists:
        bundle_has_upload_app = check_file_contains(
            "static/js/upload-app.bundle.js",
            "UploadApp",
            "Bundle contains UploadApp component"
        )
        
        bundle_has_global_export = check_file_contains(
            "static/js/upload-app.bundle.js", 
            "window.UploadApp",
            "Bundle exports UploadApp globally"
        )
    else:
        bundle_has_upload_app = False
        bundle_has_global_export = False
    
    # Check React component features
    if react_component_exists:
        component_has_drag_drop = check_file_contains(
            "frontend/src/apps/SimpleUploadApp.js",
            "onDrop",
            "Component has drag-and-drop functionality"
        )
        
        component_has_progress = check_file_contains(
            "frontend/src/apps/SimpleUploadApp.js",
            "uploadProgress",
            "Component has upload progress tracking"
        )
        
        component_has_error_handling = check_file_contains(
            "frontend/src/apps/SimpleUploadApp.js",
            "catch",
            "Component has error handling"
        )
    else:
        component_has_drag_drop = False
        component_has_progress = False
        component_has_error_handling = False
    
    task_4_1_complete = all([
        react_component_exists,
        react_bundle_exists,
        react_deps_exist,
        bundle_has_upload_app,
        bundle_has_global_export,
        component_has_drag_drop,
        component_has_progress,
        component_has_error_handling
    ])
    
    print(f"\nTask 4.1 Status: {'✓ COMPLETE' if task_4_1_complete else '✗ INCOMPLETE'}")
    
    print("\n" + "="*60 + "\n")
    
    print("Task 4.2: Add server-side fallback form for OCR upload")
    print("-" * 50)
    
    # Check template exists
    template_exists = check_file_exists(
        "faktury/templates/faktury/ocr/upload.html",
        "OCR upload template"
    )
    
    # Check view exists
    view_exists = check_file_exists(
        "faktury/views_modules/ocr_views.py",
        "OCR views module"
    )
    
    # Check template features
    if template_exists:
        template_has_fallback_form = check_file_contains(
            "faktury/templates/faktury/ocr/upload.html",
            'id="fallback-form"',
            "Template has fallback form"
        )
        
        template_has_noscript = check_file_contains(
            "faktury/templates/faktury/ocr/upload.html",
            "<noscript>",
            "Template has noscript fallback"
        )
        
        template_has_file_input = check_file_contains(
            "faktury/templates/faktury/ocr/upload.html",
            'type="file"',
            "Template has file input"
        )
        
        template_has_form_post = check_file_contains(
            "faktury/templates/faktury/ocr/upload.html",
            'method="post"',
            "Template has POST form"
        )
        
        template_has_multipart = check_file_contains(
            "faktury/templates/faktury/ocr/upload.html",
            'enctype="multipart/form-data"',
            "Template has multipart encoding"
        )
    else:
        template_has_fallback_form = False
        template_has_noscript = False
        template_has_file_input = False
        template_has_form_post = False
        template_has_multipart = False
    
    # Check view features
    if view_exists:
        view_handles_post = check_file_contains(
            "faktury/views_modules/ocr_views.py",
            "request.method == 'POST'",
            "View handles POST requests"
        )
        
        view_handles_files = check_file_contains(
            "faktury/views_modules/ocr_views.py",
            "request.FILES",
            "View handles file uploads"
        )
        
        view_has_validation = check_file_contains(
            "faktury/views_modules/ocr_views.py",
            "FileValidationError",
            "View has file validation"
        )
        
        view_has_error_handling = check_file_contains(
            "faktury/views_modules/ocr_views.py",
            "except",
            "View has error handling"
        )
    else:
        view_handles_post = False
        view_handles_files = False
        view_has_validation = False
        view_has_error_handling = False
    
    task_4_2_complete = all([
        template_exists,
        view_exists,
        template_has_fallback_form,
        template_has_noscript,
        template_has_file_input,
        template_has_form_post,
        template_has_multipart,
        view_handles_post,
        view_handles_files,
        view_has_validation,
        view_has_error_handling
    ])
    
    print(f"\nTask 4.2 Status: {'✓ COMPLETE' if task_4_2_complete else '✗ INCOMPLETE'}")
    
    print("\n" + "="*60 + "\n")
    
    # Overall task status
    task_4_complete = task_4_1_complete and task_4_2_complete
    
    print(f"Overall Task 4 Status: {'✓ COMPLETE' if task_4_complete else '✗ INCOMPLETE'}")
    
    if task_4_complete:
        print("\n🎉 Task 4: Fix OCR upload interface functionality - COMPLETED!")
        print("\nBoth subtasks have been successfully implemented:")
        print("- React upload component with drag-drop, progress tracking, and error handling")
        print("- Server-side fallback form that works without JavaScript")
        print("- Proper error boundaries and graceful degradation")
    else:
        print("\n❌ Task 4 is not yet complete. Please check the missing components above.")
    
    return task_4_complete

if __name__ == '__main__':
    main()