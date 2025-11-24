"""
Projects Routes.
Handles CRUD operations for projects.
"""
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.blueprints.projects import projects_bp
from app.forms.project_forms import ProjectForm
from app.services.project_service import ProjectService

@projects_bp.route('/')
@login_required
def list_projects():
    """List all projects for the current user."""
    try:
        projects = ProjectService.get_user_projects(current_user.id)
        return render_template('projects/list.html', projects=projects)
    except Exception as e:
        current_app.logger.error(f"Error listing projects: {str(e)}")
        flash(f"Error loading projects: {str(e)}", 'error')
        return render_template('projects/list.html', projects=[])

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project."""
    form = ProjectForm()
    
    if form.validate_on_submit():
        try:
            project_data = {
                'title': form.title.data,
                'description': form.description.data,
                'author_id': current_user.id
            }
            project_id = ProjectService.create_project(project_data)
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        except Exception as e:
            current_app.logger.error(f"Error creating project: {str(e)}")
            flash(f"Error creating project: {str(e)}", 'error')
    
    return render_template('projects/create.html', form=form)

@projects_bp.route('/<project_id>')
@login_required
def view_project(project_id):
    """View a specific project."""
    try:
        project = ProjectService.get_project(project_id)
        if not project:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.list_projects'))
        return render_template('projects/view.html', project=project)
    except Exception as e:
        current_app.logger.error(f"Error viewing project: {str(e)}")
        flash(f"Error loading project: {str(e)}", 'error')
        return redirect(url_for('projects.list_projects'))

@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit an existing project."""
    try:
        project = ProjectService.get_project(project_id)
        if not project:
            flash('Project not found.', 'error')
            return redirect(url_for('projects.list_projects'))
        
        form = ProjectForm(obj=project)
        
        if form.validate_on_submit():
            project_data = {
                'title': form.title.data,
                'description': form.description.data
            }
            ProjectService.update_project(project_id, project_data)
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        return render_template('projects/edit.html', form=form, project=project)
    except Exception as e:
        current_app.logger.error(f"Error editing project: {str(e)}")
        flash(f"Error updating project: {str(e)}", 'error')
        return redirect(url_for('projects.list_projects'))

@projects_bp.route('/<project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete a project."""
    try:
        ProjectService.delete_project(project_id)
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting project: {str(e)}")
        flash(f"Error deleting project: {str(e)}", 'error')
    
    return redirect(url_for('projects.list_projects'))
