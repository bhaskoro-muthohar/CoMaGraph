from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from uuid import UUID
from ...services.analysis_service import AnalysisService
from ...core.exceptions import ContextManagerException
from ..deps import get_analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/thread/{thread_id}/stats")
async def get_thread_statistics(
    thread_id: UUID,
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get comprehensive statistics for a thread"""
    try:
        return await analysis_service.get_thread_analytics(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/thread/{thread_id}/patterns")
async def analyze_conversation_patterns(
    thread_id: UUID,
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Analyze conversation patterns and dynamics"""
    try:
        return await analysis_service.analyze_conversation_patterns(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/thread/{thread_id}/topics")
async def get_topic_evolution(
    thread_id: UUID,
    analysis_service: AnalysisService = Depends(get_analysis_service)
) -> List[Dict[str, Any]]:
    """Analyze how topics evolve throughout the conversation"""
    try:
        return await analysis_service.get_topic_evolution(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))