import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime

class JoularReaderError(Exception):
    """Base exception class for JoularReader errors."""
    pass

class FileNotFoundError(JoularReaderError):
    """Raised when required files are not found."""
    pass

class DataParsingError(JoularReaderError):
    """Raised when there are issues parsing the data."""
    pass

class ConsumptionPoint:
    """
    Represents a single point of energy consumption measurement.
    
    Attributes:
        timestamp (float): The time at which the consumption was measured
        consumption (float): The energy consumption value in Joules
    """
    def __init__(self, timestamp: float, consumption: float):
        """
        Initialize a ConsumptionPoint with a timestamp and consumption value.
        
        Args:
            timestamp (float): The time at which the consumption was measured
            consumption (float): The energy consumption value in Joules
        """
        if not isinstance(timestamp, (int, float)):
            raise ValueError(f"Timestamp must be a number, got {type(timestamp)}")
        if not isinstance(consumption, (int, float)):
            raise ValueError(f"Consumption must be a number, got {type(consumption)}")
        if consumption < 0:
            raise ValueError(f"Consumption cannot be negative, got {consumption}")
            
        self.timestamp = timestamp
        self.consumption = consumption


class Method:
    """
    Represents a method/function with its energy consumption characteristics.
    
    Attributes:
        name (str): The full name of the method (e.g., "RayCasting.main")
        consumption (float): Total energy consumption in Joules
        percentage (float): Percentage of total application consumption
        consumption_evolution (List[ConsumptionPoint]): Time series of consumption measurements
    """
    def __init__(self, name: str, consumption: float, percentage: float, consumption_evolution: List[ConsumptionPoint]):
        """
        Initialize a Method with its consumption characteristics.
        
        Args:
            name (str): The full name of the method
            consumption (float): Total energy consumption in Joules
            percentage (float): Percentage of total application consumption
            consumption_evolution (List[ConsumptionPoint]): Time series of consumption measurements
        """
        self.name = name
        self.consumption = consumption
        self.percentage = percentage
        self.consumption_evolution = sorted(consumption_evolution, key=lambda point: point.timestamp)
        
    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Method.
        
        Returns:
            str: A formatted string showing the method's name, consumption, percentage, and number of evolution points
        """
        return f"Method: {self.name}\n" \
               f"  Total Consumption: {self.consumption:.6f} Joules\n" \
               f"  Percentage: {self.percentage:.2f}%\n" 
               
    def __repr__(self) -> str:
        """
        Returns a concise string representation of the Method.
        
        Returns:
            str: A brief string showing the method's name and consumption
        """
        return f"Method({self.name}, {self.consumption:.6f} Joules, {self.percentage:.2f}%)"

    def consumption_evolution_line_graph(self) -> None:
        """
        Plots the consumption evolution of the method as a line graph.
        
        Creates a matplotlib figure showing how the method's energy consumption
        evolved over time, with timestamps on the x-axis and consumption values
        on the y-axis.
        """
        import matplotlib.pyplot as plt

        timestamps = [point.timestamp for point in self.consumption_evolution]
        consumptions = [point.consumption for point in self.consumption_evolution]

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, consumptions, marker='o')
        plt.title(f"Consumption Evolution for Method: {self.name}")
        plt.xlabel("Timestamp")
        plt.ylabel("Consumption (Joules)")
        plt.grid(True)
        plt.show()


class CallTree:
    """
    Represents a calltree with its associated methods and total energy consumption.
    
    Attributes:
        name (str): The semicolon-separated sequence of method calls (e.g., "RayCasting.main;RayCasting.intersects")
        methods (List[Method]): List of Method objects involved in this call tree
        consumption (float): Total energy consumption of this call sequence in Joules
    """
    def __init__(self, name: str, methods: List[Method], consumption: float, percentage: float):
        """
        Initialize a CallTree with its name, methods, and consumption.
        
        Args:
            name (str): The semicolon-separated sequence of method calls
            methods (List[Method]): List of Method objects in this call tree
            consumption (float): Total energy consumption in Joules
        """
        self.name = name
        self.methods = methods
        self.consumption = consumption
        self.percentage = percentage
        
    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the CallTree.
        
        Returns:
            str: A formatted string showing the call tree's name, total consumption,
                 and details of all methods involved
        """
        methods_str = "\n".join(f"  {method}" for method in self.methods)
        return f"CallTree: {self.name}\n" \
               f"Total Consumption: {self.consumption:.6f} Joules\n" \
               f"Percentage: {self.percentage:.2f}%\n" \
               f"Methods ({len(self.methods)}):\n" \
               f"{methods_str}"
               
    def __repr__(self) -> str:
        """
        Returns a concise string representation of the CallTree.
        
        Returns:
            str: A brief string showing the call tree's name, consumption, and number of methods
        """
        return f"CallTree({self.name}, {self.consumption:.6f} Joules, {len(self.methods)} methods, {self.percentage:.2f}%)"


class JoularReader:
    """
    A class to read and parse Joular energy consumption data from CSV files.
    
    Attributes:
        root_dir (Path): The root directory containing the CSV files
        app_methods (Dict[str, Method]): Dictionary of methods from the "app" directory
        all_methods (Dict[str, Method]): Dictionary of methods from the "all" directory
        app_call_trees (Dict[str, CallTree]): Dictionary of call trees from the "app" directory
        all_call_trees (Dict[str, CallTree]): Dictionary of call trees from the "all" directory
    """
    
    def __init__(self, root_dir: Union[str, Path]):
        """
        Initialize the JoularReader with a root directory.
        
        Args:
            root_dir (Union[str, Path]): Path to the root directory containing the data files
        """
        try: 
            self.root_dir = Path(root_dir)
            self._evolution_cache = {}  # Cache for method evolution data
            self.app_methods = self._load_methods("app")
            self.all_methods = self._load_methods("all")
            self.app_call_trees = self._load_call_trees("app")
            self.all_call_trees = self._load_call_trees("all")
        except Exception as e:
            raise JoularReaderError(f"Failed to initialize JoularReader: {str(e)}")
    
    def _load_methods(self, app_name: str) -> Dict[str, Method]:
        """
        Load method-level consumption data from CSV files.
        
        Reads the method consumption CSV files from the specified application directory
        and creates Method objects for each method found.
        
        Args:
            app_name (str): The name of the application directory to read from ("app" or "all")
            
        Returns:
            Dict[str, Method]: A dictionary mapping method names to their Method objects
        """
        if app_name not in ["app", "all"]:
            raise ValueError(f"app_name must be 'app' or 'all', got {app_name}")
            
        methods_dir = self.root_dir / app_name / "total" / "methods"
        
        if not methods_dir.exists():
            raise FileNotFoundError(f"Methods directory not found: {methods_dir}")
            
        csv_files = list(methods_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {methods_dir}")
            
        methods_file = csv_files[0]
        try:
            df = pd.read_csv(
                methods_file,
                header=None,
                names=['method_path', 'consumption'],
                dtype={'method_path': str, 'consumption': float},
                usecols=[0, 1]
            )
        except pd.errors.EmptyDataError:
            raise DataParsingError(f"CSV file is empty: {methods_file}")
        except pd.errors.ParserError as e:
            raise DataParsingError(f"Failed to parse CSV file {methods_file}: {str(e)}")
        except Exception as e:
            raise JoularReaderError(f"Unexpected error reading methods file: {str(e)}")
            
        methods_dict = {}
        total_consumption = df['consumption'].sum()
        
        if total_consumption <= 0:
            raise DataParsingError("Total consumption must be positive")
            
        try:
            for method_name, method_consumption in zip(df['method_path'], df['consumption']):
                if pd.isna(method_name) or pd.isna(method_consumption):
                    continue
                    
                method_consumption_evolution = self._get_method_consumption_evolution(app_name, method_name)
                
                if method_name not in methods_dict:
                    methods_dict[method_name] = []
                methods_dict[method_name].append(Method(
                    name=method_name,
                    consumption=method_consumption,
                    percentage=(method_consumption / total_consumption) * 100,
                    consumption_evolution=method_consumption_evolution
                ))
        except Exception as e:
            raise JoularReaderError(f"Error processing methods data: {str(e)}")
            
        return methods_dict

    def _get_method_consumption_evolution(self, app_name: str, method_name: str) -> List[ConsumptionPoint]:
        """
        Load the consumption evolution data for a specific method.
        
        Reads the evolution CSV file for the given method and creates ConsumptionPoint
        objects for each timestamp-consumption pair. Uses caching to avoid re-reading files.
        
        Args:
            app_name (str): The name of the application directory to read from ("app" or "all")
            method_name (str): The name of the method to get evolution data for
            
        Returns:
            List[ConsumptionPoint]: A list of ConsumptionPoint objects representing the
                                   method's consumption evolution over time
        """
        if not isinstance(method_name, str):
            raise ValueError(f"method_name must be a string, got {type(method_name)}")
            
        cache_key = f"{app_name}:{method_name}"
        if cache_key in self._evolution_cache:
            return self._evolution_cache[cache_key]
            
        consumption_dir = self.root_dir / app_name / "evolution"
        
        if not consumption_dir.exists():
            raise FileNotFoundError(f"Evolution directory not found: {consumption_dir}")
            
        evolution_files = list(consumption_dir.glob(f"*-evolution.csv"))
        if not evolution_files:
            self._evolution_cache[cache_key] = []
            return []
            
        csv_file = evolution_files[0]
        try:
            df = pd.read_csv(
                csv_file,
                header=None,
                names=['timestamp', 'consumption'],
                dtype={'timestamp': float, 'consumption': float},
                usecols=[0, 1]
            )
            
            result = []
            for ts, cons in zip(df['timestamp'].values, df['consumption'].values):
                if pd.isna(ts) or pd.isna(cons):
                    continue
                try:
                    result.append(ConsumptionPoint(timestamp=ts, consumption=cons))
                except ValueError as e:
                    print(f"Warning: Skipping invalid data point in {csv_file}: {str(e)}")
                    continue
                    
            self._evolution_cache[cache_key] = result
            return result
            
        except pd.errors.EmptyDataError:
            raise DataParsingError(f"CSV file is empty: {csv_file}")
        except pd.errors.ParserError as e:
            raise DataParsingError(f"Failed to parse CSV file {csv_file}: {str(e)}")
        except Exception as e:
            raise JoularReaderError(f"Unexpected error reading evolution file: {str(e)}")
    
    def _load_call_trees(self, app_name: str) -> Dict[str, CallTree]:
        """
        Load call tree data from CSV files.
        
        Reads the call trees CSV file which contains sequences of method calls and their
        combined consumption. Creates CallTree objects for each unique call sequence.
        
        Args:
            app_name (str): The name of the application directory to read from ("app" or "all")
            
        Returns:
            Dict[str, CallTree]: A dictionary mapping call tree names (method sequences)
                                to their CallTree objects
        """
        if app_name not in ["app", "all"]:
            raise ValueError(f"app_name must be 'app' or 'all', got {app_name}")
            
        call_trees_dir = self.root_dir / app_name / "total" / "calltrees"
        
        if not call_trees_dir.exists():
            raise FileNotFoundError(f"Call trees directory not found: {call_trees_dir}")
            
        csv_files = list(call_trees_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {call_trees_dir}")
            
        call_trees_file = csv_files[0]
        call_trees_dict = {}
        
        try:
            df = pd.read_csv(
                call_trees_file,
                header=None,
                names=['methods_str', 'consumption'],
                dtype={'methods_str': str, 'consumption': float}
            )
            
            total_consumption = df['consumption'].sum()
            if total_consumption <= 0:
                raise DataParsingError("Total consumption must be positive")
                
            for _, row in df.iterrows():
                methods_str = row['methods_str']
                consumption = row['consumption']
                
                if pd.isna(methods_str) or pd.isna(consumption):
                    continue
                    
                method_names = methods_str.split(';')
                methods = []
                
                for method_name in method_names:
                    if method_name in self.all_methods:
                        methods.extend(self.all_methods[method_name])
                
                calltree = CallTree(
                    name=methods_str,
                    methods=methods,
                    consumption=consumption,
                    percentage=(consumption / total_consumption) * 100
                )
                call_trees_dict[methods_str] = calltree
                
        except pd.errors.EmptyDataError:
            raise DataParsingError(f"CSV file is empty: {call_trees_file}")
        except pd.errors.ParserError as e:
            raise DataParsingError(f"Failed to parse CSV file {call_trees_file}: {str(e)}")
        except Exception as e:
            raise JoularReaderError(f"Unexpected error reading call trees file: {str(e)}")
        
        return call_trees_dict