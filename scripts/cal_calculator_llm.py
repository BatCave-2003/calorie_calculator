def run():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    import pandas as pd
    import re

    # Define the model and tokenizer
    model_name = "EleutherAI/gpt-neo-1.3B"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id

    # Define the food items and create a more structured prompt
    food_items = """
    1. Apple(1 medium)
    2. Rice(1 cup)
    3. Chicken Breast(3 oz)
    4. Almonds(1 oz)
    """

    prompt = f"""
    Create a nutrition table for these foods:
    {food_items}

    Format the response exactly like this example:
    Food | Quantity | Calories | Fat(g) | Protein(g) | Carbs(g)
    Apple | 1 medium | 95 | 0.3 | 0.5 | 25
    """

    # Tokenize with proper attention mask
    inputs = tokenizer(prompt, 
                    return_tensors="pt", 
                    padding=True, 
                    truncation=True,
                    max_length=512)

    # Generate text with better parameters
    with torch.no_grad():
        output = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=512,
            min_length=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.2
        )

    # Decode and display the result
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    def parse_table_to_dataframe(text):
        try:
            # Split the text into lines and remove empty lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Find the line that contains the header (looking for 'Food | Quantity')
            header_line = None
            data_lines = []
            for line in lines:
                if 'Food' in line and '|' in line:
                    header_line = line
                    continue
                if header_line and '|' in line:
                    data_lines.append(line)
            
            if not header_line:
                raise ValueError("Could not find table header in generated text")

            # Extract headers
            headers = [h.strip() for h in header_line.split('|')]
            
            # Parse data rows
            data = []
            for line in data_lines:
                # Split by | and strip whitespace
                row = [cell.strip() for cell in line.split('|')]
                # Only add rows that have the same number of columns as headers
                if len(row) == len(headers):
                    data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # Convert numeric columns to float
            numeric_columns = ['Calories', 'Fat(g)', 'Protein(g)', 'Carbs(g)']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        
        except Exception as e:
            print(f"Error parsing table: {e}")
            return None
        
    df = parse_table_to_dataframe(generated_text)
    # print(df)
    # print(generated_text)
    if df is not None:
        print("\nPandas DataFrame:")
        print("-" * 60)
        print(df)