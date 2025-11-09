"""
Test Framework Entry Point - Supports Behave test execution
Features:
1. Execute all .feature files
2. Execute single feature file
3. Execute specified test cases by tag
4. Parallel testing
5. Allure report generation
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def run_behave(feature_file=None, tags=None, parallel=False, workers=4, format_type="allure_behave"):
    """
    Execute Behave tests
    
    Args:
        feature_file: Path to feature file to execute, if None executes all
        tags: Tags to execute, multiple tags separated by comma
        parallel: Whether to execute in parallel
        format_type: Report format
    """
    # Build behave command
    cmd = ["behave"]
    
    # Add feature file
    if feature_file:
        if not os.path.exists(feature_file):
            print(f"Error: File does not exist: {feature_file}")
            sys.exit(1)
        cmd.append(feature_file)
    else:
        # Execute all feature files
        cmd.append("features")
    
    # Add tag filter
    if tags:
        tag_list = tags.split(",")
        for tag in tag_list:
            cmd.extend(["--tags", tag.strip()])
    
    # Add format options (Allure report)
    if format_type == "allure_behave":
        cmd.extend(["--format", "allure_behave.formatter:AllureFormatter"])
        cmd.extend(["--out", "allure-results"])
    
    # Add other options
    cmd.extend(["--no-capture", "--no-capture-stderr"])
    
    # If parallel execution
    if parallel:
        try:
            # Check if behave-parallel is available
            import behave_parallel
            # Use behave parallel execution (via process pool)
            # Note: behave-parallel requires special configuration, using multiprocessing here
            import multiprocessing
            print(f"Warning: Parallel execution requires additional configuration, using serial execution")
            print("Tip: You can run different feature files simultaneously in multiple terminals for parallel execution")
            parallel = False
        except ImportError:
            print("Warning: behave-parallel not installed, cannot execute in parallel, using serial execution")
            print("Install command: pip install behave-parallel")
            parallel = False
    
    # Execute command
    print(f"Executing command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=os.getcwd())
    
    return result.returncode


def generate_allure_report():
    """Generate Allure report"""
    if not os.path.exists("allure-results"):
        print("Warning: allure-results directory does not exist, cannot generate report")
        return
    
    # Check if allure command is available
    try:
        result = subprocess.run(["allure", "--version"], capture_output=True)
        if result.returncode != 0:
            print("Warning: Allure command not available, please ensure Allure CLI tool is installed")
            return
    except FileNotFoundError:
        print("Warning: Allure command not found, please ensure Allure CLI tool is installed")
        return
    
    # Generate report
    cmd = ["allure", "generate", "allure-results", "-o", "allure-report", "--clean"]
    print(f"Generating Allure report: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("Allure report generated successfully!")
        print("Open report command: allure open allure-report")
    else:
        print("Allure report generation failed")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test framework entry point")
    parser.add_argument("-f", "--feature", help="Execute specified feature file")
    parser.add_argument("-t", "--tags", help="Execute test cases with specified tags, multiple tags separated by comma")
    parser.add_argument("-p", "--parallel", action="store_true", help="Execute tests in parallel")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of workers for parallel execution (default 4)")
    parser.add_argument("-r", "--report", action="store_true", help="Generate Allure report")
    parser.add_argument("--no-report", action="store_true", help="Do not generate Allure report")
    
    args = parser.parse_args()
    
    # Execute tests
    exit_code = run_behave(
        feature_file=args.feature,
        tags=args.tags,
        parallel=args.parallel,
        workers=args.workers
    )
    
    # Generate report
    if args.report or (not args.no_report and exit_code == 0):
        generate_allure_report()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
