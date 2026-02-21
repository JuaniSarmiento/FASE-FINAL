#!/usr/bin/env python3
"""
Script para verificar y configurar Ollama para el proyecto.
Verifica que Ollama esté corriendo y que el modelo necesario esté descargado.
"""

import requests
import sys
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://187.77.41.214:11434")
REQUIRED_MODEL = "llama3"

def check_ollama_connection():
    """Verifica si Ollama está corriendo."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama está corriendo en {OLLAMA_BASE_URL}")
            return True
        else:
            print(f"❌ Ollama respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ No se pudo conectar a Ollama en {OLLAMA_BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n📝 Para iniciar Ollama:")
        print(f"   - Local: ollama serve")
        print(f"   - Docker: docker-compose up ollama")
        return False

def check_model_availability():
    """Verifica si el modelo requerido está descargado."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            available_models = [model.get('name', '').split(':')[0] for model in models]
            
            print(f"\n📦 Modelos disponibles: {available_models}")
            
            if REQUIRED_MODEL in available_models or any(REQUIRED_MODEL in m for m in available_models):
                print(f"✅ Modelo '{REQUIRED_MODEL}' está disponible")
                return True
            else:
                print(f"⚠️  Modelo '{REQUIRED_MODEL}' NO está disponible")
                print(f"\n📝 Para descargar el modelo:")
                print(f"   ollama pull {REQUIRED_MODEL}")
                return False
    except Exception as e:
        print(f"❌ Error verificando modelos: {e}")
        return False

def check_chroma_connection():
    """Verifica si ChromaDB está corriendo."""
    chroma_host = os.getenv("CHROMA_DB_HOST", "localhost")
    chroma_port = os.getenv("CHROMA_DB_PORT", "8001")
    chroma_url = f"http://{chroma_host}:{chroma_port}"
    
    try:
        # ChromaDB expone /api/v1/heartbeat
        response = requests.get(f"{chroma_url}/api/v1/heartbeat", timeout=5)
        if response.status_code == 200:
            print(f"✅ ChromaDB está corriendo en {chroma_url}")
            return True
        else:
            print(f"⚠️  ChromaDB respondió con código {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"⚠️  No se pudo conectar a ChromaDB en {chroma_url}")
        print(f"   ChromaDB es necesario para procesamiento de PDFs")
        print(f"\n📝 Para iniciar ChromaDB:")
        print(f"   docker-compose up chroma")
        return False

def main():
    print("🔍 Verificando configuración de IA para el proyecto...\n")
    
    ollama_ok = check_ollama_connection()
    if ollama_ok:
        model_ok = check_model_availability()
    else:
        model_ok = False
    
    print()
    chroma_ok = check_chroma_connection()
    
    print("\n" + "="*60)
    print("📊 RESUMEN:")
    print("="*60)
    print(f"Ollama:       {'✅ OK' if ollama_ok else '❌ NO DISPONIBLE'}")
    print(f"Modelo {REQUIRED_MODEL}: {'✅ OK' if model_ok else '❌ NO DISPONIBLE'}")
    print(f"ChromaDB:     {'✅ OK' if chroma_ok else '⚠️  NO DISPONIBLE (opcional para desarrollo)'}")
    
    if not ollama_ok or not model_ok:
        print("\n⚠️  ADVERTENCIA: La generación de ejercicios con IA no funcionará sin Ollama y el modelo.")
        sys.exit(1)
    elif not chroma_ok:
        print("\n⚠️  ADVERTENCIA: El procesamiento de PDFs no funcionará sin ChromaDB.")
        print("   Puedes iniciar solo Ollama para generar ejercicios sin PDFs.")
        sys.exit(0)
    else:
        print("\n✅ Todo configurado correctamente. El sistema está listo.")
        sys.exit(0)

if __name__ == "__main__":
    main()
