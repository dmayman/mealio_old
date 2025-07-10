"""Household API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.schemas import (
    Household, HouseholdCreate, HouseholdUpdate, HouseholdWithMembers,
    HouseholdMembership, HouseholdMembershipUpdate, 
    HouseholdJoinRequest, APIResponse
)
from app.services import HouseholdService
from app.models import User

router = APIRouter(prefix="/households", tags=["households"])

# Mock dependency for current user - replace with actual auth
async def get_current_user() -> User:
    """Mock current user dependency."""
    # In production, this would extract user from JWT token
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User"
    )


@router.post("/", response_model=Household, status_code=status.HTTP_201_CREATED)
async def create_household(
    household_data: HouseholdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new household."""
    try:
        household = await HouseholdService.create_household(db, current_user.id, household_data)
        return household
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create household: {str(e)}"
        )


@router.get("/current", response_model=HouseholdWithMembers)
async def get_current_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the user's current household."""
    household = await HouseholdService.get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not in a household"
        )
    return household


@router.get("/{household_id}", response_model=HouseholdWithMembers)
async def get_household(
    household_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific household."""
    household = await HouseholdService.get_household(db, household_id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    
    # Check if user is a member of this household
    user_household = await HouseholdService.get_user_household(db, current_user.id)
    if not user_household or user_household.id != household_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this household"
        )
    
    return household


@router.put("/{household_id}", response_model=Household)
async def update_household(
    household_id: uuid.UUID,
    household_data: HouseholdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a household."""
    # Check if household exists
    household = await HouseholdService.get_household(db, household_id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    
    # Check if user is admin of this household
    user_membership = None
    for member in household.members:
        if member.user_id == current_user.id:
            user_membership = member
            break
    
    if not user_membership or user_membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can update household details"
        )
    
    updated_household = await HouseholdService.update_household(db, household_id, household_data)
    return updated_household


@router.post("/join", response_model=HouseholdMembership, status_code=status.HTTP_201_CREATED)
async def join_household(
    join_request: HouseholdJoinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a household using an invite code."""
    try:
        membership = await HouseholdService.join_household(db, current_user.id, join_request.invite_code)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid invite code"
            )
        return membership
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to join household: {str(e)}"
        )


@router.post("/leave", response_model=APIResponse)
async def leave_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave the current household."""
    success = await HouseholdService.leave_household(db, current_user.id)
    if success:
        return APIResponse(success=True, message="Successfully left household")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not in a household"
        )


@router.put("/{household_id}/members/{user_id}", response_model=HouseholdMembership)
async def update_member_role(
    household_id: uuid.UUID,
    user_id: uuid.UUID,
    membership_data: HouseholdMembershipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a member's role in the household."""
    # Check if household exists and user is admin
    household = await HouseholdService.get_household(db, household_id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    
    # Check if current user is admin of this household
    user_membership = None
    for member in household.members:
        if member.user_id == current_user.id:
            user_membership = member
            break
    
    if not user_membership or user_membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can update member roles"
        )
    
    # Update the member's role
    updated_membership = await HouseholdService.update_member_role(
        db, household_id, user_id, membership_data.role
    )
    
    if not updated_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in household"
        )
    
    return updated_membership


@router.delete("/{household_id}/members/{user_id}", response_model=APIResponse)
async def remove_member(
    household_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from the household."""
    # Check if household exists and user is admin
    household = await HouseholdService.get_household(db, household_id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    
    # Check if current user is admin of this household
    user_membership = None
    for member in household.members:
        if member.user_id == current_user.id:
            user_membership = member
            break
    
    if not user_membership or user_membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can remove members"
        )
    
    # Prevent removing yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from household. Use leave endpoint instead."
        )
    
    # Remove the member
    success = await HouseholdService.remove_member(db, household_id, user_id)
    
    if success:
        return APIResponse(success=True, message="Member removed from household")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in household"
        )