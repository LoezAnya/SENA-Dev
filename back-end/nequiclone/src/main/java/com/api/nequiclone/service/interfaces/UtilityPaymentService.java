package com.api.nequiclone.service.interfaces;

import java.util.List;

import com.api.nequiclone.entity.UtilityProvider;
import com.api.nequiclone.enums.UtilityCategory;

public interface UtilityPaymentService {
    
List<UtilityCategory> getAllCategories();

List<UtilityProvider> getActiveProvidersByCategory(UtilityCategory category);
}
