import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def delete_entry(title):
    """
    Deletes an encyclopedia entry, given its title 
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def convert_markdown(text):
    """
    Converts markdown sybnax into html.
    Only headings, unordered list, paragraphs, links and bold text.
    """
    # Split string into lines
    lines = re.split(r"\n", text)

    # Calcluate lenght of lines list and set booleans, that shows if current iteration is in or outside of the html tag
    list_lenght =len(lines)
    list_tag = False
    p_tag = False

    new_string = ""

    # Iterate over splited string
    for index, line in enumerate(lines):
        # Headings
        if re.match(r"#", line):
            # Calculate heading number
            repeats = len(re.findall("#", line))

            # Substitute '#' and insert it in front of string
            line = re.sub(f"{repeats * '#'}", f"<h{repeats}>", line)

            # Insert closing tag
            line = line + f"</h{repeats}>"
        
        # Unordered list - outside the ul tag
        elif re.match(r"\*", line) and not list_tag:
            # Insert tag in front of list item
            line = "<ul>" + line

            # Substitute '*' with li tag and add closing tag at the end of the line
            line = re.sub(r"\*", "<li>", line)
            line = line + "</li>"

            # Set the bool indicating that we are inside of <ul> tag
            list_tag = True

        # Unordered list - insdie of <ul> tag
        elif re.match(r"\*", line) and list_tag:
            # Insert tag in front of list item
            line = re.sub(r"\*", "<li>", line)
            line = line + "</li>"

            # Check if next line is still a list item, if not add a closing </ul> tag
            if index + 1 < list_lenght and not re.match(r"\*", lines[index + 1]):
                line = line + "</ul>"

                # Indicate that we left the <ul> tag
                list_tag = False
        
        # Paragraph - not list, not heading -> paragraph. Opening the tag
        elif re.match(r"\w", line) and not p_tag:
            line = "<p>" + line

            # Indicate that we are inside the tag
            p_tag = True

        # If we beggining with empty line that means we ended previous paragraph
        elif re.match("", line) and p_tag:
            # Add end tag
            line = line + "</p>"

            # Indicate we are outside the tag
            p_tag = False

        # Bold text - search for boldtext indication
        while re.search(r"\*\*", line):
            # First match opens the tag
            line = re.sub(r"\*\*", "<b>", line, 1)

            # Secound match closes the tag
            line = re.sub(r"\*\*", "</b>", line, 1)

        # Search for expression "[...](...)"
        while re.search(r"\[(.*?)\]\((.*?)\)", line):
            # Assign tags attributes to variables
            a_text = re.findall(r"\[(.*?)\]\(", line)
            a_link = re.findall(r"\]\((.*?)\)", line)

            # Insert attributes into formated string and substitute it in text
            a_tag = f'<a href="{a_link[0]}">{a_text[0]}</a>' 
            line = re.sub(r"\[(.*?)\]\((.*?)\)", a_tag, line, 1)

        # Save the new string
        new_string += line 

    return new_string