package com.api.nequiclone.dto.request;

import java.math.BigDecimal;

import lombok.Getter;
import lombok.Setter;


@Getter
@Setter
public class UtilityPaymentRequestDTO {
    private long providerId;
    private long contractNumber;
    private BigDecimal amount;
}
