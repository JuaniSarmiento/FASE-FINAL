#!/usr/bin/env python3
"""
Script para iniciar el entorno de desarrollo local.
Verifica configuración y inicia servicios necesarios.
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description, check_output=False):
    """Ejecuta un comando y muestra resultado."""
    print(f"\n🔄 {description}...")
    try:
        if check_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(f"⚠️  Advertencia: {result.stderr}")
            return result.returncode == 0
        else:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ {description} - Completado")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en: {description}")
        print(f"   {str(e)}")
        return False

def check_docker():
    """Verifica que Docker esté instalado y corriendo."""
    print("\n🐳 Verificando Docker...")
    result = subprocess.run("docker --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Docker no está instalado. Instala Docker Desktop desde https://docker.com")
        return False
    print("✅ Docker está instalado")
    
    # Verificar que Docker esté corriendo
    result = subprocess.run("docker ps", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Docker no está corriendo. Inicia Docker Desktop.")
        return False
    print("✅ Docker está corriendo")
    return True

def check_ollama():
    """Verifica que Ollama esté instalado."""
    print("\n🤖 Verificando Ollama...")
    result = subprocess.run("ollama --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("⚠️  Ollama no está instalado")
        print("📝 Instalar desde: https://ollama.ai")
        print("   Después ejecuta: ollama pull llama3")
        return False
    print("✅ Ollama está instalado")
    return True

def main():
    print("="*60)
    print("🚀 INICIO DEL ENTORNO DE DESARROLLO")
    print("="*60)
    
    # 1. Verificar Docker
    if not check_docker():
        sys.exit(1)
    
    # 2. Verificar Ollama
    ollama_installed = check_ollama()
    
    # 3. Iniciar servicios Docker (DB y ChromaDB)
    print("\n📦 Iniciando servicios Docker (PostgreSQL y ChromaDB)...")
    if not run_command("docker-compose up -d db chroma", "Iniciar DB y ChromaDB"):
        print("❌ No se pudieron iniciar los servicios. Verifica docker-compose.yml")
        sys.exit(1)
    
    # Esperar a que los servicios estén listos
    print("\n⏳ Esperando a que los servicios estén listos (10 segundos)...")
    time.sleep(10)
    
    # 4. Verificar servicios de IA
    print("\n🔍 Verificando configuración de IA...")
    if not run_command("python check_ai_services.py", "Verificar IA", check_output=True):
        print("\n⚠️  Algunos servicios de IA no están disponibles")
        print("   El backend puede iniciar pero la generación de ejercicios no funcionará")
        response = input("\n¿Deseas continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            sys.exit(1)
    
    # 5. Instrucciones finales
    print("\n" + "="*60)
    print("✅ ENTORNO LISTO")
    print("="*60)
    print("\n📝 Próximos pasos:")
    print("\n1. Iniciar el backend:")
    print("   python -m uvicorn src.infrastructure.http.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n2. Iniciar el frontend:")
    print("   cd frontend")
    print("   npm run dev")
    print("\n3. Abrir navegador:")
    print("   http://localhost:5173")
    
    if ollama_installed:
        print("\n4. Si Ollama no está corriendo, abre otra terminal y ejecuta:")
        print("   ollama serve")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Proceso interrumpido por el usuario")
        sys.exit(0)
