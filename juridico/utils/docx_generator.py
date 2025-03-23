import os
import uuid
from num2words import num2words
from docx import Document
import re
from copy import deepcopy
from typing import Optional, Union, Dict, Any, List

# Constants
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_PATH = os.path.join(PARENT_DIR, 'docs')
OUTPUT_PATH = os.path.join(PARENT_DIR, 'output')

# Global Dictionaries (Consider using classes or a more encapsulated approach if this becomes more complex)
COUNTER_DICT: Dict[int, int] = {}
SUBCOUNTER_DICT: Dict[int, Dict[int, int]] = {}

COUNTERS: Dict[str, int] = {}  # Initialize the counters dictionary

def create_table_around_value(paragraph, value: str):
    """
    Creates a simple table around the given value within a Word document paragraph.

    Args:
        paragraph: The docx.paragraph.Paragraph object where the table will be inserted.
        value: The string value to be placed inside the table.

    Returns:
        The original paragraph, for chaining or further manipulation.
    """
    table = paragraph.add_paragraph().add_run().add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    cell.text = value
    table.style = 'Table Grid'
    return paragraph


def convert_number_to_text(value: Optional[Union[int, float, str]]) -> str:
    """
    Converts a numerical value to its textual representation in Brazilian Portuguese.

    Args:
        value: The numerical value to convert. Can be an integer, float, or string.  None is accepted and returns "".

    Returns:
        The textual representation of the number, or an empty string if conversion fails.
    """
    if value is None:
        return ""
    try:
        value_str = str(value).replace('.', '').replace(' ', '')
        return num2words(int(value_str), lang='pt_BR')
    except ValueError:
        return ""

def replace_text(paragraph, field: str, value: str):
    """
    Replaces all occurrences of {field} in the paragraph with the given value.

    Args:
        paragraph: The docx.paragraph.Paragraph object to modify.
        field: The string representing the placeholder to replace (e.g., 'name').
        value: The string value to insert in place of the placeholder.
    """
    formatted_field = f"{{{field}}}"
    if formatted_field in paragraph.text:
        new_text = paragraph.text.replace(formatted_field, str(value) if value else "")
        paragraph.clear()
        paragraph.add_run(new_text)

def parse_string(input_str: str) -> tuple[str, Optional[str], Optional[str]]:
    """
    Parses a string to extract components based on delimiters ":" and "/".

    Args:
        input_str: The string to parse (e.g., "x:y/modifier" or "x/modifier" or "x").

    Returns:
        A tuple containing x, y (optional), and modifier (optional).
    """
    if ":" in input_str:
        x, rest = input_str.split(":", 1)
        if "/" in rest:
            y, modifier = rest.split("/")
        else:
            y = rest
            modifier = None
        return x, y, modifier
    elif "/" in input_str:
        x, modifier = input_str.split("/")
        return x, None, modifier
    else:
        return input_str, None, None

def apply_rules_to_value(value: Any, yaml_data: Dict[str, Any], field_verified: str, doc: Document, data: Dict[str, Any], yaml: Dict[str, Any], index: str | None = None) -> Any:
    """
    Applies rules to a value based on configurations in the YAML file.

    Args:
        value: The initial value to be processed.
        yaml_data: The YAML data containing rules and configurations.
        field_verified: The field being verified (used for context in rules).
        doc: The Document object (used if rules require document context).
        data: The data dictionary containing values for formatting.
        yaml: The entire YAML configuration for broader context access.
        index (str | None): O índice, que pode ser uma string ou None.
    Returns:
        The modified value after applying all relevant rules.
    """
    if not yaml_data.get('regras'):
        return value

    for rule_obj in yaml_data.get('regras', []):
        if isinstance(rule_obj, dict):
            for rule, rule_value in rule_obj.items():
                if rule == "Add_box" and rule_value:
                    pass  # Placeholder for future action
                elif rule == "Number_To_Text" and isinstance(rule_value, str):
                    value_to_convert = data.get(rule_value)
                    if value_to_convert is not None:
                        value = convert_number_to_text(value_to_convert)
                elif rule == "Formater" and isinstance(rule_value, str):
                    value = format_text_with_data(rule_value, data, yaml, index)
                elif rule == "Counter" and isinstance(rule_value, str):
                    value = handle_counter_rule(rule_value, value)

    return value

def format_text_with_data(format_string: str, data: Dict[str, Any], yaml: Dict[str, Any], index: str | None = None) -> str:
    """
    Formats a string using values from the provided data dictionary and YAML configurations.

    Args:
        format_string: The string containing placeholders to be replaced.
        data: The dictionary containing data values.
        yaml: The YAML configuration for accessing document-level configurations.
        index (str | None): O índice, que pode ser uma string ou None.

    Returns:
        The formatted string.
    """
    def replace_variable(match):
        key = match.group(1)

        # Try to find the value in the `data` dictionary
        if key in data and data[key] is not None:
            return str(data[key])
        else:
            # Look up in the YAML within `Documentos-Config`
            document_configs = yaml.get('Documentos', {}).get('Documentos-Config', [])
            item_filtered = next((item for item in document_configs if item.get('nome') == key), None)

            if item_filtered:
                if item_filtered.get('regras') or item_filtered.get('condicao'):
                    if not verify_conditions(data, item_filtered, None, index):
                        return ""

                    variables_yaml = item_filtered.get('variaveis', [])
                    new_value = variables_yaml[0] if variables_yaml else None

                    if new_value is None:
                        new_value = apply_rules_to_value(None, item_filtered, key, None, data, None)

                    return str(new_value) if new_value is not None else match.group(0)

        return ""

    return re.sub(r'{(.*?)}', replace_variable, format_string)

def handle_counter_rule(rule_value: str, value: Any) -> str:
    """
    Handles the counter rule by parsing the rule value and updating the counter.

    Args:
        rule_value: The string containing the counter rule (e.g., "x:y/B").
        value: The current value to which the counter value will be prepended.

    Returns:
        The updated value with the counter prepended.
    """
    if rule_value:
        x, y, modifier = parse_string(rule_value)
        counter_value = get_counter_value(x, y)
        if modifier == "B":
            counter_value = f"**{counter_value} - **"
        return counter_value + str(value)  # Ensure value is converted to string

    return str(value)  # Ensure value is converted to string

def get_counter_value(x: str, y: Optional[str] = None) -> str:
    """
    Retrieves and increments counter values based on x and y identifiers.

    Args:
        x: The primary counter identifier.
        y: The secondary counter identifier (optional).

    Returns:
        The string representation of the counter value.
    """
    x_int = int(x)
    y_int = int(y) if y is not None else None

    if x_int not in COUNTER_DICT:
        COUNTER_DICT[x_int] = 1
        SUBCOUNTER_DICT[x_int] = {}

    if y_int is not None:
        if y_int not in SUBCOUNTER_DICT[x_int]:
            SUBCOUNTER_DICT[x_int][y_int] = 1
        else:
            SUBCOUNTER_DICT[x_int][y_int] += 1
        return f"{COUNTER_DICT[x_int] - 1}.{SUBCOUNTER_DICT[x_int][y_int]}"

    if y == 'Y' and x == '0':
        x_int = 1

    current_value = COUNTER_DICT[x_int]
    COUNTER_DICT[x_int] += 1

    return str(current_value)

def replace_match(match: re.Match) -> str:
    """
    Replaces a regex match with a counter value.

    Args:
        match: The regex match object.

    Returns:
        The string representation of the new counter value.
    """
    x = match.group(1)
    y = match.group(2)
    new_value = get_counter_value(x, y) if y else get_counter_value(x)
    return str(new_value)

def process_data(data: Dict[str, Any], parsed_data_options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes data based on parsed data options to create new data entries.

    Args:
        data: The original data dictionary.
        parsed_data_options: Configuration options for processing data.

    Returns:
        A new dictionary with processed data.
    """
    new_data = {}
    counters = {}

    print("Processing data")
    for name, config in parsed_data_options.items():
        if name in data:
            value = data[name]
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if key not in counters:
                                counters[key] = 0
                            else:
                                counters[key] += 1
                            new_key = f"form-{counters[key]}-{key}"
                            new_data[new_key] = val
                    else:
                        new_key = f"form-{i}-{name}"
                        new_data[new_key] = item
            elif isinstance(value, dict):
                for key, val in value.items():
                    if key not in counters:
                        counters[key] = 0
                    else:
                        counters[key] += 1
                    new_key = f"form-{counters[key]}-{key}"
                    new_data[new_key] = val
            else:
                new_key = f"form-0-{name}"
                new_data[new_key] = value

    return new_data

def process_special_inputs(original_text: str) -> str:
    """
    Processes special inputs in the text to format them correctly, incrementing counters for repeated names.

    Args:
        original_text: The original text containing special inputs (e.g., "{#Nome}").

    Returns:
        The processed text with formatted special inputs (e.g., "{form-0-Nome}", "{form-1-Nome}").
    """

    def replace_input(match: re.Match) -> str:
        """
        Replaces a match with the formatted input, incrementing the counter if the name is repeated.
        """
        name: str = match.group(1)  # Extract the name from the match
        if name.startswith('form-'):
            # If already in the format {form-X-Nome}, do not alter it
            return match.group(0)

        if name not in COUNTERS:
            # If the name is encountered for the first time, initialize its counter
            COUNTERS[name] = 0
        else:
            # If the name has appeared before, increment its counter
            COUNTERS[name] += 1

        # Return the new formatted string
        return f"{{form-{COUNTERS[name]}-{name}}}"

    # Pattern to capture {#Nome} or {any-prefix-Nome} but prioritize {#Nome}
    pattern = r'{(?:#|\w+-)(\w+)}'

    processed_text: str = re.sub(pattern, replace_input, original_text)

    return processed_text

def extract_name(key: str) -> str:
    """
    Extracts the name from a formatted key string.

    Args:
        key: The formatted key string (e.g., "form-0-name").

    Returns:
        The extracted name (e.g., "name").
    """
    parts = key.split('-')
    return '-'.join(parts[2:])

def replace_variables_in_paragraph(paragraph: object, data: Dict[str, Any], yaml_data: Dict[str, Any], doc: object, parsed_data_options: Dict[str, Any], row: object = None, table_o: object = None) -> object:
    """
    Replaces variables in a paragraph, handling counters and conditional formatting.

    Args:
        paragraph: The docx.paragraph.Paragraph object to process.
        data: The dictionary containing data values.
        yaml_data: The YAML configuration for accessing document configurations.
        doc: The Document object.
        parsed_data_options: Configuration options for data processing.
        row: The table row object (if the paragraph is in a table).
        table_o: The table object (if the paragraph is in a table).

    Returns:
        The modified paragraph object.
    """
    # Extract the entire text from the paragraph's runs
    original_text = "".join(run.text for run in paragraph.runs)

    # Process special inputs
    processed_text = process_special_inputs(original_text)

    # Clear existing runs in the paragraph
    for run in paragraph.runs:
        run.text = ""

    # Add the processed text back to the paragraph
    new_run = paragraph.add_run(processed_text) # Create only one new run
    
    # Regular expression to find patterns like {counter:x} or {counter:x:y}
    counter_pattern = r"{counter:(\d+)(?::(\d+))?}"

    # Substitute directly in the runs of the paragraph
    for run in paragraph.runs:
        if "{counter:" in run.text:
            run.text = re.sub(counter_pattern, replace_match, run.text)

    # Process other variables besides counters
    for key, value in data.items():
        formatted_key = f"{{{key}}}"

        # Check if the formatted key exists in the processed text BEFORE attempting to replace it
        if formatted_key in new_run.text:  # Changed to new_run.text
            print(f"Special key found: {formatted_key}")

            # Get the reformatted key (removing "form-X-" prefix if it exists)
            reformatted_key = extract_name(key) if key.startswith("form") else key
            index = key.split('-')[1] if key.startswith("form") else None

            # Look up the item configuration from the YAML file
            document_configs = yaml_data.get('Documentos', {}).get('Documentos-Config', [])
            item_filtered = next((item for item in document_configs if item.get('nome') == reformatted_key), None)

            # If there are conditions and they are not met, skip the replacement
            if item_filtered and not verify_conditions(data, item_filtered, reformatted_key, index):
                new_run.text = new_run.text.replace(formatted_key, '')
                continue

            # Get the new value to replace the formatted key with
            new_value = str(value) if value is not None else ''
            if not new_value and item_filtered and item_filtered.get('variaveis'):
                new_value = str(item_filtered['variaveis'][0]) if item_filtered['variaveis'][0] is not None else ''

            # Apply rules to the new value
            if item_filtered:
                new_value = apply_rules_to_value(new_value, item_filtered, reformatted_key, doc, data, yaml_data, index)

            # Replace the formatted key with the new value
            if formatted_key in new_run.text:  # Double-check that the key is still in the text
                new_text = new_run.text.replace(formatted_key, str(new_value))

                # Handle bold text markers
                if "**" in new_text:
                    parts = new_text.split("**")
                    new_run.text = ""
                    for i, part in enumerate(parts):
                        run = paragraph.add_run(part)
                        if i % 2 == 1:
                            run.bold = True
                else:
                    new_run.text = new_text

                # Remove the row if the new text is empty
                if table_o is not None and not new_text.strip():
                    for row in table_o.rows:
                        if all(not cell.text.strip() for cell in row.cells):
                            table_o._tbl.remove(row._tr)
                            break

    # Recognize counters inside tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    for run in par.runs:
                        if "{counter:" in run.text:
                            run.text = re.sub(counter_pattern, replace_match, run.text)

    return paragraph

def replace_variables_in_tables(doc: Document, data: Dict[str, Any], yaml_data: Dict[str, Any], parsed_data_options: Dict[str, Any]):
    """Replaces variables inside tables of the document."""
    for table_index, table in enumerate(doc.tables):
        for row_index, row in enumerate(table.rows):
            for cell_index, cell in enumerate(row.cells):
                for paragraph in cell.paragraphs:
                    replace_variables_in_paragraph(paragraph, data, yaml_data, doc, parsed_data_options, row, table)

def replace_variables_in_footers(doc: Document, data: Dict[str, Any], yaml_data: Dict[str, Any], parsed_data_options: Dict[str, Any]):
    """Replaces variables in the footers of the document."""
    for section in doc.sections:
        for footer in section.footer.paragraphs:
            replace_variables_in_paragraph(footer, data, yaml_data, doc, parsed_data_options)

def replace_variables_in_headers(doc: Document, data: Dict[str, Any], yaml_data: Dict[str, Any], parsed_data_options: Dict[str, Any]):
    """Replaces variables in the headers of the document."""
    for section in doc.sections:
        for header in section.header.paragraphs:
            replace_variables_in_paragraph(header, data, yaml_data, doc, parsed_data_options)


def verify_conditions(data: Dict[str, Any], yaml_data: Dict[str, Any], field_verified: str, index: str | None = None) -> bool:
    """
    Verifies conditions for a field based on YAML configurations, adjusting keys if field_verified starts with "form-".

    Args:
        data: The dictionary containing data values.
        yaml_data: The YAML configuration data.
        field_verified: The field being verified.
        index (str | None): O índice, que pode ser uma string ou None.

    Returns:
        True if all conditions are met or no conditions are specified, False otherwise.
    """
    try:
        condition = yaml_data.get('condicao', {})

        if not condition:
            return True

        if not isinstance(condition, dict):
            return False

        for key, value in condition.items():
            adjusted_key = key  # Initialize adjusted_key with the original key

            # Check if index is not None 
            if index is not None:
                adjusted_key = f"form-{index}-{key}"

            if '/' in adjusted_key:
                keys = adjusted_key.split('/')
                condition_met = False

                for key_part in keys:
                    if key_part in data:
                        field_value = data[key_part]

                        if isinstance(value, list):
                            if field_value in value:
                                condition_met = True
                                break
                        elif isinstance(value, bool):
                            if value and not field_value:
                                return False
                            elif not value and field_value:
                                return False
                        else:
                            if isinstance(field_value, str) and isinstance(value, str):
                                if field_value == value:
                                    condition_met = True
                                    break
                            elif field_value == value:
                                condition_met = True
                                break


                if not condition_met:
                    return False

            else:
                if adjusted_key in data:
                    field_value = data[adjusted_key]

                    if isinstance(value, list):
                        if field_value not in value:
                            return False
                    elif isinstance(value, bool):
                        if value and not field_value:
                            return False
                        elif not value and field_value:
                            return False
                    else:
                        if isinstance(field_value, str) and isinstance(value, str):
                            if field_value != value:
                                return False
                        elif field_value != value:
                            return False

                else:
                    return False

        return True
    except Exception as e:
        print("Error in verify_conditions")
        raise

def insert_table_after(original_table: object, new_table: object):
    """Inserts a new table after the original table in the document."""
    original_table_element = original_table._element
    new_table_element = new_table._element
    original_table_element.addnext(new_table_element)

def insert_row_below(table: object, original_row: object):
    """Inserts a new row below the original row in the table."""
    new_row = table.add_row()

    for i, cell in enumerate(original_row.cells):
        new_row.cells[i].text = ""

def generate_docx(data: Dict[str, Any], folder: str, yaml_data: Dict[str, Any], parsed_data_options: Dict[str, Any]) -> str:
    """
    Generates a DOCX file by populating a template with data from a form and YAML configurations.

    Args:
        data: The dictionary containing data to populate the document.
        folder: The folder containing the DOCX template.
        yaml_data: The YAML data containing document configurations.
        parsed_data_options: Options for parsing and processing data.

    Returns:
        The path to the generated DOCX file.
    """
    template_path = os.path.abspath(os.path.join(DOCS_PATH, folder, f'{folder}.docx'))
    unique_id = str(uuid.uuid4())[:8]

    # Add YAML variables to data if they don't already exist
    for yaml_field in yaml_data.get('Documentos', {}).get('Documentos-Config', []):
        field_name = yaml_field.get('nome')
        if field_name and field_name not in data:
            if not yaml_field.get('grupo'):
                data[field_name] = None

    # Load the DOCX file
    try:
        doc = Document(template_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_path}")
    except Exception as e:
        raise Exception(f"Error loading document: {e}")

    # Table cloning logic
    for group in parsed_data_options:
        if group in data:
            print(f"Group: {group}")
            search_text = parsed_data_options[group].get('buscador')
            print(f"Search text: {search_text}")
            multiplier = data[group]
            num_dicts = sum(1 for item in multiplier if isinstance(item, dict))
            num_dicts -= 1

            if num_dicts > 0:
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if search_text in cell.text:
                                original_table = table
                                for _ in range(num_dicts):
                                    new_table = deepcopy(original_table)
                                    insert_table_after(original_table, new_table)
                                    print("New table inserted after original.")
                                break

    # Data processing
    print("Processing data")
    processed_data = process_data(data, parsed_data_options)
    data.update(processed_data)
    for group in parsed_data_options:
        del data[group]

    if not doc.paragraphs:
        raise ValueError(f"The template {template_path} contains no paragraphs.")

    # Variable substitution
    for paragraph in doc.paragraphs:
        replace_variables_in_paragraph(paragraph, data, yaml_data, doc, parsed_data_options)

    replace_variables_in_tables(doc, data, yaml_data, parsed_data_options)
    replace_variables_in_footers(doc, data, yaml_data, parsed_data_options)
    replace_variables_in_headers(doc, data, yaml_data, parsed_data_options)

    # Save the generated file
    output_filename = f'{folder}_preenchido_{unique_id}.docx'
    output_path_formatted = os.path.abspath(os.path.join(OUTPUT_PATH, output_filename))
    doc.save(output_path_formatted)

    return output_filename