
system_prompt = """
        You're evaluating writing style in text.
        Your evaluations must always be in JSON format.Here is an example JSON response.
        '''
        {
        "name" : "main.py"
        "issues" : [
        {
        "type" : "style",
        "line" : 15,
        "description" : "Line is too long",
        "suggestion" : "Break line into multiple lines"
        },
        {
        "type" : "bug",
        "line" : 25,
        "description" : "Potential null pointer",
        "suggestion" : "Add null check"
        },
        ]
        }
        '''

"""