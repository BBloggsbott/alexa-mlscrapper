mkdir packages
pip install --target ./packages/ -r requirements.txt
zip -r9 function.zip packages/*
zip -g function.zip lambda_function.py