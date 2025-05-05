import markdown2
import logging
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self):
        # Dynamically determine the root path of the project
        self.root_dir = Path(__file__).resolve().parent.parent  # app directory
        self.templates_dir = self.root_dir / 'templates' / 'emails'
        
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            logger.warning(f"Email templates directory not found at {self.templates_dir}")

    def _read_template(self, template_name: str) -> str:
        """Private method to read template content.
        
        Args:
            template_name: Name of the template (without extension)
            
        Returns:
            str: Template content as string
        """
        template_path = self.templates_dir / f"{template_name}.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error(f"Template not found: {template_path}")
            # Return a simple fallback template
            return "<html><body><h1>{{ title }}</h1><p>{{ content }}</p></body></html>"

    def render_template(self, template_name: str, **kwargs) -> str:
        """Render a template with the given context variables.
        
        Args:
            template_name: Name of the template (without extension)
            **kwargs: Template variables to substitute
            
        Returns:
            str: Rendered HTML content
        """
        # Map simplified template names to actual template files
        template_map = {
            'email_verification': 'email_verification',
            'password_reset': 'password_reset',
            'account_locked': 'account_locked',
            'account_unlocked': 'account_unlocked',
            'role_upgrade': 'role_upgrade',
            'professional_status': 'professional_status'
        }
        
        # Get the actual template file name
        template_file = template_map.get(template_name, template_name)
            
        try:
            # Read the template content
            template_content = self._read_template(template_file)
            
            # Simple template substitution using string replace
            # This is a basic approach; in a more complex application, consider using jinja2
            for key, value in kwargs.items():
                placeholder = '{{ ' + key + ' }}'
                template_content = template_content.replace(placeholder, str(value))
                
            return template_content
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            # Return a simple fallback template with error details
            return f"<html><body><h1>Error rendering template</h1><p>{str(e)}</p></body></html>"

    def _apply_email_styles(self, html: str) -> str:
        """Apply advanced CSS styles inline for email compatibility with excellent typography."""
        styles = {
            'body': 'font-family: Arial, sans-serif; font-size: 16px; color: #333333; background-color: #ffffff; line-height: 1.5;',
            'h1': 'font-size: 24px; color: #333333; font-weight: bold; margin-top: 20px; margin-bottom: 10px;',
            'p': 'font-size: 16px; color: #666666; margin: 10px 0; line-height: 1.6;',
            'a': 'color: #0056b3; text-decoration: none; font-weight: bold;',
            'footer': 'font-size: 12px; color: #777777; padding: 20px 0;',
            'ul': 'list-style-type: none; padding: 0;',
            'li': 'margin-bottom: 10px;'
        }
        # Wrap entire HTML content in <div> with body style
        styled_html = f'<div style="{styles["body"]}">{html}</div>'
        # Apply styles to each HTML element
        for tag, style in styles.items():
            if tag != 'body':  # Skip the body style since it's already applied to the <div>
                styled_html = styled_html.replace(f'<{tag}>', f'<{tag} style="{style}">')
        return styled_html

    def render_template(self, template_name: str, **context) -> str:
        """Render a markdown template with given context, applying advanced email styles."""
        header = self._read_template('header.md')
        footer = self._read_template('footer.md')

        # Read main template and format it with provided context
        main_template = self._read_template(f'{template_name}.md')
        main_content = main_template.format(**context)

        full_markdown = f"{header}\n{main_content}\n{footer}"
        html_content = markdown2.markdown(full_markdown)
        return self._apply_email_styles(html_content)
