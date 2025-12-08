package com.api.nequiclone.dto.request;

import java.math.BigDecimal;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DepositRequestDTO {
    @NotNull(message = "accountId es requerido")
    private Long accountId;
    
    @NotNull(message = "amount es requerido")
    @Positive(message = "amount debe ser positivo")
    private BigDecimal amount;
    
    private String description;
}