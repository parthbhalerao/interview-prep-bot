from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = (
    'You are tasked with extracting specific information from the following text content: {dom_content}'
    'Please follow these instrunctions carefully: \n\n'
    '1. **Extract Information:** Only extract information that directly matches the provided description: {parse_description}'
    '2. **No extra content:** Only extract information that directly matches the provided description'
    '3. **Empty Response:** If no information matches the description, return an empty string ('').'
    '4. **Direct data only:** Your output should contain only the data that is explicitly requested, no other information should be extracted'
    '5. **No your instructions:** Your output should contain only the data and the answer rather than saying that you are showing only the information I requested'
    '6. **Message Language:** Also ensure that the output is formatted in a way where its short and can be sent as a message. '
)

model = OllamaLLM(model='llama3.1')

def parse_with_ollama(dom_chunks, parse_description):
    # Create the prompt template
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        # Combine dom_content and parse_description into a single input dictionary
        input_data = {
            'dom_content': chunk,
            'parse_description': parse_description
        }

        # Invoke the chain with the combined input dictionary
        response = chain.invoke(input_data)
        print(f'Parsed batch {i} of {len(dom_chunks)}')

        parsed_results.append(response)

    # Join all results into a single output
    return '\n'.join(parsed_results)