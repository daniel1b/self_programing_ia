import yaml
import re
from typing import Dict, List, Any, Union, Optional
from abc import ABC, abstractmethod
from src.llm.ModeloLLM import ModeloLLM

class PipelineContext:
    """Manages the context/state during pipeline execution"""
    
    def __init__(self, dict_input):
        if isinstance(dict_input, str):
            self._data = {'user_input': dict_input}
        elif isinstance(dict_input, dict):
            self._data = dict_input.copy()
        else:
            raise ValueError("Input must be a string or a dictionary.")
    
    def get(self, key: str) -> Any:
        """Get a value from the context"""
        return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the context"""
        self._data[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all data in the context"""
        return self._data.copy()

class StepProcessor(ABC):
    """Base class for processing different step types"""
    
    @abstractmethod
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> Any:
        """Process a step and return its result"""
        pass
    
    def _resolve_input(self, input_value: Union[str, List[str]], context: PipelineContext) -> Any:
        """Resolve input references from the context"""
        if isinstance(input_value, list):
            return [context.get(item) for item in input_value]
        return context.get(input_value)
    
    def _substitute_variables(self, template: str, context: PipelineContext, item: Any = None) -> str:
        """Replace {variables} in templates with values from context"""
        result = template
        
        # First handle regular context variables
        pattern = r'\{([^{}]+)\}'
        for match in re.finditer(pattern, template):
            var_name = match.group(1)
            if var_name in context.get_all():
                result = result.replace(f"{{{var_name}}}", str(context.get(var_name)))
        
        # Handle special {item} variable for loop operations
        if item is not None:
            result = result.replace("{item}", str(item))
            
        return result

class LLMStepProcessor(StepProcessor):
    """Processes steps of type 'llm'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> str:
        input_value = self._resolve_input(step_config["input"], context)
        prompt = self._substitute_variables(step_config["prompt"], context)
        
        # Call the LLM with the prompt using ModeloLLM
        result = llm_model.enviar_prompt(prompt)
        return result

class ReasonStepProcessor(StepProcessor):
    """Processes steps of type 'raciocinar'"""

    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> str:
        input_value = self._resolve_input(step_config["input"], context)
        reasoning_template = step_config["prompt"]
        
        # Substitui variáveis no prompt
        prompt = self._substitute_variables(reasoning_template, context)

        # Opcional: Adiciona contexto extra
        if isinstance(input_value, list):
            contexto_completo = "\n".join(str(item) for item in input_value)
            prompt = f"Contexto:\n{contexto_completo}\n\n\n{prompt}"

        # Chama o modelo com o prompt de raciocínio
        result = llm_model.enviar_prompt(prompt)
        return result


class LoopLLMStepProcessor(StepProcessor):
    """Processes steps of type 'loop_llm'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> List[str]:
        inputs = step_config["input"]
        
        if not isinstance(inputs, list):
            raise ValueError("O campo 'input' de 'loop_llm' deve ser uma lista de variáveis.")
        
        resolved_inputs = [self._resolve_input(i, context) for i in inputs]
        
        # Identifica o primeiro item iterável
        iterable_index = None
        for idx, val in enumerate(resolved_inputs):
            if isinstance(val, list):
                if iterable_index is not None:
                    raise ValueError("Apenas um item do 'input' pode ser uma lista iterável.")
                iterable_index = idx
        
        if iterable_index is None:
            raise ValueError("Nenhum item iterável encontrado no input para 'loop_llm'.")

        loop_key = inputs[iterable_index]
        loop_values = resolved_inputs[iterable_index]

        # Cria um dicionário base com os valores fixos
        static_inputs = {
            inputs[i]: resolved_inputs[i]
            for i in range(len(inputs))
            if i != iterable_index
        }

        results = []
        for item in loop_values:
            # Define a variável iterável no contexto temporariamente
            context.set(loop_key, item)
            for k, v in static_inputs.items():
                context.set(k, v)

            prompt = self._substitute_variables(step_config["prompt"], context, item)
            result = llm_model.enviar_prompt(prompt)
            results.append(result)

        return results

class ExtractListStepProcessor(StepProcessor):
    """Processes steps of type 'extract_list'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> List[str]:
        input_value = self._resolve_input(step_config["input"], context)
        prompt = self._substitute_variables(step_config["prompt"], context)
        
        # Ask LLM to extract list items
        response = llm_model.enviar_prompt(prompt)
        
        # Simple parsing of list items (adjust based on LLM output format)
        list_items = [item.strip() for item in response.split('\n') if item.strip()]
        return list_items

class ConcatStepProcessor(StepProcessor):
    """Processes steps of type 'concat'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> str:
        input_values = self._resolve_input(step_config["input"], context)
        
        # Se o valor de entrada for uma lista, concatena os itens em uma única string.
        if isinstance(input_values, list):
            concatenated = "\n".join(str(item) for item in input_values)
        else:
            concatenated = str(input_values)
        
        if "prompt" in step_config:
            prompt_template = step_config["prompt"]
            
            # Cria um dicionário de substituição baseado no contexto atual.
            substitutions = context.get_all()
            
            # Se 'input' no YAML for uma lista, substituímos cada chave encontrada nela
            # com a versão concatenada; se for string, fazemos a mesma substituição.
            if isinstance(step_config["input"], list):
                for key in step_config["input"]:
                    substitutions[key] = concatenated
            elif isinstance(step_config["input"], str):
                substitutions[step_config["input"]] = concatenated
            
            # Realiza a substituição dos placeholders no prompt template.
            prompt_result = prompt_template
            for key, value in substitutions.items():
                prompt_result = prompt_result.replace(f"{{{key}}}", str(value))
            return prompt_result
        else:
            # Se nenhum prompt for especificado, retorna o valor concatenado.
            return concatenated


class ConditionalStepProcessor(StepProcessor):
    """Processes steps of type 'conditional'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> Any:
        condition = step_config["condition"]
        input_value = self._resolve_input(step_config["input"], context)
        
        # Evaluate the condition
        condition_prompt = self._substitute_variables(condition["prompt"], context)
        condition_result = llm_model.enviar_prompt(condition_prompt)
        
        # Simplified condition evaluation (assuming LLM returns "yes" or "no")
        if condition_result.strip().lower() in ["yes", "true", "1", "sim"]:
            if "then_prompt" in condition:
                then_prompt = self._substitute_variables(condition["then_prompt"], context)
                return llm_model.enviar_prompt(then_prompt)
        else:
            if "else_prompt" in condition:
                else_prompt = self._substitute_variables(condition["else_prompt"], context)
                return llm_model.enviar_prompt(else_prompt)
        
        return None

class BranchStepProcessor(StepProcessor):
    """Processes steps of type 'branch'"""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> List[Any]:
        branches = step_config["branches"]
        results = []
        
        for branch in branches:
            branch_input = self._resolve_input(branch.get("input", step_config["input"]), context)
            branch_prompt = self._substitute_variables(branch["prompt"], context)
            
            # Execute the branch
            branch_result = llm_model.enviar_prompt(branch_prompt)
            results.append(branch_result)
        
        return results

class PipelineStepProcessor(StepProcessor):
    """Processes steps of type 'pipeline', executing a sub-pipeline defined in a YAML file."""
    
    def process(self, step_config: Dict[str, Any], context: PipelineContext, llm_model: ModeloLLM) -> Any:
        # Resolver o input para o sub-pipeline (por exemplo, 'respostas_relevantes')
        sub_input = self._resolve_input(step_config["input"], context)
        
        # Obter o path do pipeline secundário a partir do step_config
        pipeline_path = step_config.get("path")
        if not pipeline_path:
            raise ValueError("Para o step do tipo 'pipeline', é necessário definir o 'path' do arquivo YAML.")
        
        # Cria uma instância do sub-pipeline usando o path fornecido e o mesmo llm_model
        sub_pipeline = CognitivePipeline(pipeline_path, llm_model)
        
        # Executa o sub-pipeline com o sub_input como entrada
        sub_result = sub_pipeline.execute(sub_input)
        
        # Retorna o resultado que será armazenado no contexto do pipeline pai
        return sub_result


class CognitivePipeline:
    """Main class for processing the cognitive pipeline"""
    
    def __init__(self, yaml_path: str, llm_model: Optional[ModeloLLM] = None):
        """
        Initialize the pipeline
        
        Args:
            yaml_path: Path to the YAML file defining the pipeline
            llm_model: ModeloLLM instance for LLM interactions (if None, a default one will be created)
        """
        self.yaml_path = yaml_path
        self.pipeline_config = self._load_yaml(yaml_path)
        
        # Use provided ModeloLLM or create a default one
        self.llm_model = llm_model if llm_model else ModeloLLM()
        
        # Register step processors
        self.step_processors = {
            "llm": LLMStepProcessor(),
            "loop_llm": LoopLLMStepProcessor(),
            "extract_list": ExtractListStepProcessor(),
            "concat": ConcatStepProcessor(),
            "conditional": ConditionalStepProcessor(),
            "branch": BranchStepProcessor(),
            "pipeline": PipelineStepProcessor(),
            "raciocinar": ReasonStepProcessor()  # <- Novo tipo aqui
        }


        # Initialize execution log
        self.execution_log = []
    
    def _load_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """Load and parse the YAML file"""
        try:
            with open(yaml_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load pipeline configuration: {e}")
    
    def execute(self, dict_input) -> Any:
        """
        Execute the pipeline with the given user input
        
        Args:
            user_input: The initial user input text
            
        Returns:
            The final output of the pipeline
        """
        context = PipelineContext(dict_input)
        self.execution_log = []  # Reset execution log
        
        # Execute each step in order
        for step_config in self.pipeline_config["pipeline"]:
            step_id = step_config["step"]
            step_type = step_config["type"]
            
            try:
                # Get the appropriate processor for this step type
                processor = self.step_processors.get(step_type)
                if not processor:
                    raise ValueError(f"Unknown step type: {step_type}")
                
                # Execute the step
                result = processor.process(step_config, context, self.llm_model)
                
                # Store the result in context if output is specified
                if "output" in step_config:
                    context.set(step_config["output"], result)
                
                # Log the execution
                self.execution_log.append({
                    "step": step_id,
                    "type": step_type,
                    "result": result
                })
                
            except Exception as e:
                error_msg = f"Error processing step '{step_id}': {str(e)}"
                self.execution_log.append({
                    "step": step_id,
                    "type": step_type,
                    "error": error_msg
                })
                raise RuntimeError(error_msg)
        
        # Return the final result (last step's output)
        if self.execution_log:
            final_step = self.pipeline_config["pipeline"][-1]
            if "output" in final_step:
                return context.get(final_step["output"])
            else:
                return self.execution_log[-1]["result"]
        
        return None
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log of the pipeline"""
        return self.execution_log
    
    def alterar_modelo_llm(self, novo_modelo: str) -> None:
        """
        Altera o modelo de linguagem utilizado pelo LLM
        
        Args:
            novo_modelo: Nome do novo modelo a ser utilizado
        """
        self.llm_model.alterar_modelo(novo_modelo)
    
    def alterar_temperatura_llm(self, nova_temperatura: float) -> None:
        """
        Altera a temperatura do modelo de linguagem
        
        Args:
            nova_temperatura: Novo valor de temperatura (entre 0.0 e 1.0)
        """
        self.llm_model.alterar_temperatura(nova_temperatura)
